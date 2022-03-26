venv: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install pip-tools

compile.in:
	.venv/bin/pip-compile -r requirements.in

sync:
	.venv/bin/pip-sync

format:
	.venv/bin/black .
	.venv/bin/isort .

data/list:
	.venv/bin/python src/download_list.py

data/films: data/list
	.venv/bin/python src/download_films.py
