.DEFAULT_GOAL := help

HOST ?= 0.0.0.0
PORT ?= 8000
ENV_FILE ?= .local.env
DOWNGRADE_VERSION ?= base
SRC := handlers/

## Lint code
lint:
	@echo "Linting code..."
	poetry run ruff check $(SRC) --fix

## Format code using Black + isort
format:
	@echo "🎨 Formatting with black and isort..."
	poetry run black $(SRC)
	poetry run isort $(SRC)

## Check code style without fixing (flake8, mypy, black --check, isort --check)
style-check:
	@echo "🔍 Checking with flake8..."
	poetry run flake8 $(SRC)
	@echo "🧠 Type checking with mypy..."
	poetry run mypy $(SRC)
	@echo "🕵️ Black format check..."
	poetry run black --check $(SRC)
	@echo "🧹 isort check..."
	poetry run isort --check $(SRC)

## All checks and formatting
check: lint format style-check
## Install Python dependencies
install:
	@echo "Installing python dependencies..."
	python3 -m pip install poetry
	poetry install

## Activate virtual environment
activate:
	@echo "Activating virtual environment..."
	poetry shell

## Add dependency
add:
	@echo "Installing dependency $(LIBRARY)"
	poetry add $(LIBRARY)

## Setup project
setup: install activate

## Run Docker containers
run-docker:
	docker compose up -d

## Stop Docker containers
stop-docker:
	docker compose down

## Build containers
build-docker:
	docker compose build
## Rebuild Docker containers
rebuild-docker:
	docker compose down -v
	docker compose build
	docker compose up -d


### Run backend using Poetry
#run-back:
#	@echo "$$(tput bold)Starting backend:$$(tput sgr0)"
#	poetry run uvicorn main:app --host $(HOST) --port $(PORT) --reload --env-file $(ENV_FILE)
#
### Run full backend environment
#run: run-docker run-back

## Migrations
migrate-create:
	docker compose exec app alembic revision --autogenerate -m "$(MIGRATION)"

migrate-apply:
	docker compose exec app alembic upgrade head


## Show migration history
migrate-history:
	@echo "📚 Showing migration history..."
	#alembic history --verbose
	docker compose exec app alembic history --verbose


migrate-downgrade:
	docker compose exec app alembic downgrade $(DOWNGRADE_VERSION)

## Run tests
test:
	@echo "Running tests..."
	poetry run pytest tests/ -v



## Clean cache files
clean:
	@echo "Cleaning cache files..."
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache

## Show help
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $$(uname) = Darwin && echo '--no-init --raw-control-chars')


## Initialize the database with test data
init-db:
	@echo "⏳ Initializing DB with data..."
	docker compose exec app poetry run python utils/add_data_to_db.py