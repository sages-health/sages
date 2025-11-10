VENV_FOLDER = .venv
PROMPT = vims

update: | $(VENV_FOLDER)
	$(VENV_FOLDER)/bin/pip install -e .

build: | $(VENV_FOLDER)
	$(VENV_FOLDER)/bin/python3 -m build

clean:
	rm -rf .venv

distclean: clean
	rm -rf dist

$(VENV_FOLDER):
	python3 -m venv --prompt $(PROMPT) $@
	$(VENV_FOLDER)/bin/pip install -U pip
	$(VENV_FOLDER)/bin/pip install -U setuptools
	$(VENV_FOLDER)/bin/pip install -U wheel build
	$(VENV_FOLDER)/bin/pip install \
		black==22.3.0 \
		isort==5.10.1 \
		flake8==4.0.1 \
		pre-commit
	$(VENV_FOLDER)/bin/pre-commit install

.PHONY: update build clean distclean
