BLACK=black -l78

all: lint

lint:
	$(BLACK) --check .

black:
	$(BLACK) .
