venv: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install pip-tools
	.venv/bin/pip install -e .

compile.setup: .venv
	.venv/bin/pip-compile

sync: .venv
	.venv/bin/pip-sync --pip-args "-e ."

format:
	.venv/bin/black .
	.venv/bin/isort .

data/list:
	.venv/bin/python src/download_list.py

data/films: data/list
	.venv/bin/python src/download_films.py

data/grossing_list.csv: data/films
	.venv/bin/python src/generate_csv.py
