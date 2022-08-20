test:
	pytest testing/

quality_checks: test
	isort testing
	black testing
	pylint --recursive=y testing

move_code: quality_checks
	cp testing/covid_PredMonitor.py  delivery
