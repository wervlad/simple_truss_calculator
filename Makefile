SOURCES = $(wildcard *.py) $(wildcard */*.py)
EXECUTABLE = run.py
INTERPRETER = python3

run: $(EXECUTABLE)
	$(INTERPRETER) $(EXECUTABLE)

tests:
	behave

coverage_measure:
	coverage run --source='.' -m behave
	coverage report

coverage_measure_html:
	coverage run --source='.' -m behave
	coverage html
	@xdg-open htmlcov/index.html

tags:
	ctags -f tags -R --fields=+iaS --extras=+q $(SOURCES)

include_tags:
	ctags -f include_tags -R --languages=python --fields=+iaS --extras=+q \
		/usr/lib/python3.7/

clean:
	rm -rf tags include_tags __pycache__ */__pycache__ */*/__pycache__ \
		.mypy_cache */.mypy_cache */*/.mypy_cache .coverage htmlcov

.PHONY: clean tags tests
