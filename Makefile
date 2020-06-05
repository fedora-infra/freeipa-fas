BLACK=black -l78
ESLINT=eslint

all: lint

lint:
	$(BLACK) --check .
	$(ESLINT) ui/js/plugins/

black:
	$(BLACK) .
