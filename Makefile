SOURCES = $(wildcard *.py) $(wildcard */*.py)
EXECUTABLE = run.pyw
INTERPRETER = python3

run: $(EXECUTABLE)
	$(INTERPRETER) $(EXECUTABLE)

tests: system_tests unit_tests

system_tests:
	behave

unit_tests:
	$(INTERPRETER) run_unit_tests.py

coverage_measure:
	coverage run run_unit_tests.py
	coverage report

coverage_measure_html:
	coverage run run_unit_tests.py
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

.PHONY: clean tags unit_tests
