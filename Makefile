.PHONY: test test-debug build-dev

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
