.PHONY: test test-debug build-dev build shell

test:
	docker-compose run --rm app sh -c "\
		poetry install && \
		poetry run isort . --check && \
		poetry run black . --check && \
		poetry run mypy . && \
		poetry run pytest"

test-debug:
	docker-compose run --rm app sh -c "\
		poetry install && \
		poetry run pytest -s"

build-dev:
	mv dist dist-tmp &&\
		poetry build &&\
		mv dist/*.whl ../coordservice/coordextract-local/ &&\
		cp dist-tmp/* dist/ &&\
		rm -rf dist-tmp

build:
	docker build -t smcleaish/coordextract .

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down --volumes --rmi coordextract

shell:
	docker-compose run --rm app /bin/bash

coordextract: build up
