import re
from pathlib import Path
from typing import Iterator, NamedTuple

from bs4 import BeautifulSoup
from bs4.element import Tag


class Film(NamedTuple):
    rank: int
    title: str
    file_info_url: str
    worldwide_lifetime_gross: int
    domestic_lifetime_gross: int
    domestic_percentage: float
    foreign_lifetime_gross: int
    foreing_percentage: float
    year: int

    @staticmethod
    def parse_row(raw_info: Tag) -> "Film":
        row_iter = iter(raw_info.children)

        def get_text() -> str:
            return next(row_iter).get_text()

        rank = int(get_text())
        title_row = next(row_iter)
        title = title_row.get_text()
        file_info_url = title_row.a.attrs["href"]
        worldwide_lifetime_gross = int(re.sub(r"[,$]", "", get_text()))
        domestic_lifetime_gross = int(re.sub(r"[,$]", "", get_text()))
        domestic_percentage = float(get_text().replace("%", "")) / 100
        foreign_lifetime_gross = int(re.sub(r"[,$]", "", get_text()))
        foreign_percentage = float(get_text().replace("%", "")) / 100
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
    for film in scrap_films():
        print(film)


if __name__ == "__main__":
    main()
