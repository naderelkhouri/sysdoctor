.PHONY: install test lint clean build run

install:
	pip install -e .

test:
	python3 -m unittest discover -s tests

lint:
	python3 -m sysdoctor --report

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ __pycache__/ sysdoctor/__pycache__/ sysdoctor/*/__pycache__

build:
	python3 -m build 2>/dev/null || pip install build && python3 -m build

run:
	python3 -m sysdoctor
