BLACK=black -l78

all: lint

lint:
	$(BLACK) --check .
	jsl -nologo -nosummary -process ui/js/plugins/userfas/userfas.js

black:
	$(BLACK) .
