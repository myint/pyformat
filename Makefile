check:
	pep8 pyformat.py setup.py
	pep257 pyformat.py setup.py
	pylint \
		--reports=no \
		--disable=invalid-name \
		--rcfile=/dev/null \
		pyformat.py setup.py
	check-manifest
	python setup.py --long-description | rst2html --strict > /dev/null
	scspell pyformat.py setup.py test_pyformat.py README.rst

coverage:
	@coverage erase
	@PYFORMAT_COVERAGE=1 coverage run \
		--branch --parallel-mode --omit='*/site-packages/*' \
		test_pyformat.py
	@coverage combine
	@coverage report

open_coverage: coverage
	@coverage html
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

mutant:
	@mut.py -t pyformat -u test_pyformat -mc

readme:
	@restview --long-description --strict
