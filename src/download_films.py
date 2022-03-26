import time

import requests

from src.common import DataPaths, sanitize_file_name, scrap_film_rows

BASE_URL = "https://www.boxofficemojo.com"


def main():
    if not DataPaths.FILMS.is_dir():
        DataPaths.FILMS.mkdir(parents=True)
    for film in scrap_film_rows():
        film_info_url = f"{BASE_URL}{film.file_info_url}"
        film_path = DataPaths.FILMS / f"{sanitize_file_name(film.title)}.html"

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
