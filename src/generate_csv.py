import csv
import re
from pathlib import Path

import requests

from src.common import FilmInfo, scrap_film_info, scrap_film_rows, sleep_scrap


def fetch_rating(film_info: FilmInfo) -> tuple[str | None, str | None]:
    rating_url = f"https://www.imdb.com/title/{film_info.film_row.imdb_id}/parentalguide"
    response = requests.get(rating_url)
    sleep_scrap()

    if not response.ok:
        print(
            f"ERROR: Response not OK from {rating_url}\n"
            f"Status: {response.status_code}\n"
            f"Body:\n"
            f"{response.content}"
        )
        return None, None

    # Try MPA rating
    us_rating_pattern = r"United States:([\-PGR13NC7]+)<"
    us_rating_groups = re.findall(us_rating_pattern, response.content.decode())
    if us_rating_groups:
        return "MPAA", us_rating_groups[0]

    # Try MDA rating
    sg_rating_pattern = r"Singapore:([GP13NC6M8R2]+)<"
    sg_rating_groups = re.findall(sg_rating_pattern, response.content.decode())
    if sg_rating_groups:
        return "MDA", sg_rating_groups[0]

    print(f"INFO: Could not fetch rating for '{film_info.film_row.title}'")
    return None, None


def main() -> None:
    csv_path = Path(__file__).parent.parent / "data" / "grossing_list.csv"
    with csv_path.open(mode="w") as csv_fp:
        writer = csv.writer(csv_fp)
        writer.writerow(
            [
                "RANK",
                "TITLE",
                "IMDB_ID",
                "WORLDWIDE_LIFETIME_GROSS",
                "DOMESTIC_LIFETIME_GROSS",
                "DOMESTIC_PERCENTAGE",
                "FOREIGN_LIFETIME_GROSS",
                "FOREIGN_PERCENTAGE",
                "YEAR",
                "MPAA",
                "MDA",
            ]
        )
        for film_row in scrap_film_rows():
            info = scrap_film_info(film_row)
            if info.mpaa in ("G", "PG", "PG-13", "R", "NC-17"):
                mpaa = info.mpaa
                mda = None
            else:
                rating_type, rating = fetch_rating(info)
                match rating_type:
                    case "MPAA":
                        mpaa = rating
                        mda = None
                    case "MDA":
                        mpaa = None
                        mda = rating
                    case None:
                        mpaa = None
                        mda = None
                    case _:
                        raise Exception(f"Unknown rating {rating_type}")
            writer.writerow(
                [
                    info.film_row.rank,
                    info.film_row.title,
                    info.film_row.imdb_id,
                    info.film_row.worldwide_lifetime_gross,
                    info.film_row.domestic_lifetime_gross,
                    info.film_row.domestic_percentage,
                    info.film_row.foreign_lifetime_gross,
                    info.film_row.foreign_percentage,
                    info.film_row.year,
                    mpaa,
                    mda,
                ]
            )


if __name__ == "__main__":
    main()
