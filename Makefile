venv: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -U pip setuptools wheel
	.venv/bin/pip install pip-tools
