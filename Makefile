check:
	pycodestyle pyformat.py setup.py
	pydocstyle pyformat.py setup.py
	pylint \
		--rcfile=/dev/null \
		--errors-only \
		pyformat.py setup.py
	check-manifest
	rstcheck README.rst
	scspell pyformat.py setup.py test_pyformat.py README.rst

coverage:
	@coverage erase
	@PYFORMAT_COVERAGE=1 coverage run \
		--branch --parallel-mode \
                --omit='*/distutils/*,*/site-packages/*' \
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
