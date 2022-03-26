import csv
from pathlib import Path

from src.common import scrap_film_info, scrap_film_rows


def main() -> None:
    csv_path = Path(__file__).parent.parent / "data" / "grossing_list.csv"
    with csv_path.open(mode="w") as csv_fp:
        writer = csv.writer(csv_fp)
        writer.writerow(
            [
                "RANK",
                "TITLE",
                "WORLDWIDE_LIFETIME_GROSS",
                "DOMESTIC_LIFETIME_GROSS",
                "DOMESTIC_PERCENTAGE",
                "FOREIGN_LIFETIME_GROSS",
                "FOREIGN_PERCENTAGE",
                "YEAR",
                "MPAA",
            ]
        )
        for film_row in scrap_film_rows():
            info = scrap_film_info(film_row)
            writer.writerow(
                [
                    info.film_row.rank,
                    info.film_row.title,
                    info.film_row.worldwide_lifetime_gross,
                    info.film_row.domestic_lifetime_gross,
                    info.film_row.domestic_percentage,
                    info.film_row.foreign_lifetime_gross,
                    info.film_row.foreign_percentage,
                    info.film_row.year,
                    info.mpaa,
                ]
            )


if __name__ == "__main__":
    main()
