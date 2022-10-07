## Lint your code using pylint
.PHONY: lint
lint:
	python -m pylint --version
	python -m pylint twitter_bot --output-format colorized
## Run tests using pytest
.PHONY: test
test:
	python -m pytest --version
	python -m pytest tests
## Format your code using black
.PHONY: black
black:
	python -m black --version
	python -m black .
## Run ci part
.PHONY: ci
    ci: lint black test
