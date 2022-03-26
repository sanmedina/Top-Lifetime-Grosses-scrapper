import re
import time
from pathlib import Path
from typing import Iterator, NamedTuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = "https://www.boxofficemojo.com"


class Film(NamedTuple):
    rank: int
    title: str
    file_info_url: str
    worldwide_lifetime_gross: int | None
    domestic_lifetime_gross: int | None
    domestic_percentage: float | None
    foreign_lifetime_gross: int | None
    foreign_percentage: float | None
    year: int

    @staticmethod
    def parse_row(raw_info: Tag) -> "Film":
        row_iter = iter(raw_info.children)

        def get_text() -> str:
            return next(row_iter).get_text()

        def parse_gross(value: str) -> int | None:
            if value == "-":
                return None
            return int(re.sub(r"[,$]", "", value))

        def parse_percentage(value: str) -> float | None:
            if value == "-":
                return None
            return float(re.sub(r"[%<]", "", value)) / 100

        rank = int(re.sub(",", "", get_text()))
        title_row = next(row_iter)
        title = title_row.get_text()
        file_info_url = title_row.a.attrs["href"]
        worldwide_lifetime_gross = parse_gross(get_text())
        domestic_lifetime_gross = parse_gross(get_text())
        domestic_percentage = parse_percentage(get_text())
        foreign_lifetime_gross = parse_gross(get_text())
        foreign_percentage = parse_percentage(get_text())
        year = int(get_text())

        return Film(
            rank,
            title,
            file_info_url,
            worldwide_lifetime_gross,
            domestic_lifetime_gross,
            domestic_percentage,
            foreign_lifetime_gross,
            foreign_percentage,
            year,
        )


def iter_html_files() -> Iterator[Path]:
    html_files = Path(__file__).parent.parent / "data" / "list"
    for html_path in sorted(html_files.glob("*.html")):
        yield html_path


def scrap_films() -> Iterator[Film]:
    for html_path in iter_html_files():
        with html_path.open(mode="r") as html_fp:
            soup = BeautifulSoup(html_fp.read(), "lxml")
        children_iter = iter(soup.table.children)

        # Get header
        header = next(children_iter)
        columns = list(header.children)
        print(f"Number of columns: {len(columns)}")
        print("Columns:")
        for column in columns:
            print(column.span.get_text())

        for raw_info in children_iter:
            yield Film.parse_row(raw_info)


def main():
    films_dir_path = Path(__file__).parent.parent / "data" / "films"
    if not films_dir_path.is_dir():
        films_dir_path.mkdir(parents=True)
    for film in scrap_films():
        film_info_url = f"{BASE_URL}{film.file_info_url}"
        film_path = films_dir_path / f"{film.title.replace('/', '--')}.html"

        if film_path.exists():
            continue

        response = requests.get(film_info_url)
        if not response.ok:
            raise Exception(
                "Server did not answered an OK status. Answer was:\n"
                f"URL: {film_info_url}\n"
                f"Status: {response.status_code}\n"
                f"Body: {response.content}"
            )

        with film_path.open(mode="wb") as film_fp:
            film_fp.write(response.content)

        time.sleep(2)


if __name__ == "__main__":
    main()
