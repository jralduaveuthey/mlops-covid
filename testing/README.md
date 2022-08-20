# testing
Moved deployment+monitoring/covid_pred+monitor.py to this folder renaming it to testing/covid_PredMonitor.py.
The file with the flows had to be renamed to covid_PredMonitor.py because pytest complained of the previous name.
Setting VS Code as explained in the Module 6 one can see the unit test. No integration test yet.

Run unit test in  testing/covid_PredMonitor_test.py. To reproduce it run in the terminal from the top level of the repo:
```
pipenv run pytest testing
```

Best practices like linting and formating are also applied in this folder as well as in the pre-commit hooks
