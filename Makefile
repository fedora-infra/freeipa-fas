BLACK=black -l78
JSL=jsl -nologo -nosummary

all: lint

lint:
	$(BLACK) --check .
	$(JSL) -process ui/js/plugins/userfas/userfas.js
	$(JSL) -process ui/js/plugins/groupfas/groupfas.js

black:
	$(BLACK) .
