.PHONY: lint
lint:
	mypy deppy

.PHONY: test
test:
	pytest deppy -v