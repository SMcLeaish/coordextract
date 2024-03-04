.PHONY: tests

tests:
	docker-compose run --rm app sh -c "\
		poetry install && \
		poetry run isort . --check && \
		poetry run black . --check && \
		poetry run mypy . && \
		poetry run pytest"

