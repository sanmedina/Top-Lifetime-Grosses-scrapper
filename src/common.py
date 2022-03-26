import re
from pathlib import Path
from typing import Iterator, NamedTuple

from bs4 import BeautifulSoup
from bs4.element import Tag


class DataPaths:
    LIST = Path(__file__).parent.parent / "data" / "list"
    FILMS = Path(__file__).parent.parent / "data" / "films"


class FilmRow(NamedTuple):
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
    def parse_row(raw_info: Tag) -> "FilmRow":
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

        return FilmRow(
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


class FilmInfo(NamedTuple):
    film_row: FilmRow
    mpaa: str | None


def iter_html_files() -> Iterator[Path]:
    html_files = DataPaths.LIST
    for html_path in sorted(html_files.glob("*.html")):
        yield html_path


def scrap_film_rows() -> Iterator[FilmRow]:
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
            yield FilmRow.parse_row(raw_info)


def scrap_film_info(film_row: FilmRow) -> FilmInfo:
    film_path = DataPaths.FILMS / f"{sanitize_file_name(film_row.title)}.html"
    with film_path.open(mode="r") as film_fp:
        soup = BeautifulSoup(film_fp.read(), "lxml")

    mpaa_element = soup.find(text="MPAA")
    mpaa = mpaa_element.next.get_text() if mpaa_element else None
    return FilmInfo(film_row, mpaa)


def sanitize_file_name(name: str) -> str:
    return f"{name.replace('/', '--')}"
