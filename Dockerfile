FROM python:3.11
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-root 
COPY . /app
CMD ["poetry", "run", "pytest"]
