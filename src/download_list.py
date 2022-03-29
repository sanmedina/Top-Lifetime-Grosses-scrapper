from pathlib import Path

import requests

from src.common import TIME_SLEEP, sleep_scrap

TOP_GROSSING_URL = "https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/"


def main():
    data_dir_path = Path(__file__).parent.parent / "data" / "list"
    if not data_dir_path.is_dir():
        data_dir_path.mkdir(parents=True)

    for offset in [0, 200, 400, 600, 800]:
        offset_param = "" if offset == 0 else f"?offset={offset}"
        url = f"{TOP_GROSSING_URL}{offset_param}"
        response = requests.get(url)
        if not response.ok:
            raise Exception(
                "Server did not answered an OK status. Answer was:\n"
                f"URL: {url}\n"
                f"Status: {response.status_code}\n"
                f"Body: {response.content}"
            )

        offset_html_path = data_dir_path / f"offset-{offset}.html"
        with offset_html_path.open(mode="wb") as offset_fp:
            offset_fp.write(response.content)

        print(f"{url} downloaded. Waiting {TIME_SLEEP} secs...")
        sleep_scrap()


if __name__ == "__main__":
    main()
