BLACK=black

all: lint

lint:
	$(BLACK) --check .

black:
	$(BLACK) .
