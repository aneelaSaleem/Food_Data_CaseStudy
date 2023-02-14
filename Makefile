.PHONY: all

all: setup lint test run
setup:
	pip -q install pipenv
	pipenv install

lint:
	pipenv run isort .
	pipenv run flake8 --exclude=*.pyc,__pycache__ --max-line-length 130 food_data_processor/
	pipenv run flake8 --exclude=*.pyc,__pycache__ --max-line-length 130 tests

test:
	pipenv run pytest

run:
	pipenv run python main.py

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	pipenv --rm