# testing
Moved deployment+monitoring/covid_pred+monitor.py to this folder renaming it to testing/covid_PredMonitor.py.
Run unit test in  testing/covid_PredMonitor_test.py. To reproduce it run in the terminal from the top level of the repo:
```
pipenv run pythest testing
```

# Makefile
This file takes the "testing/covid_PredMonitor.py" file and creates a new folder under the folder /delivery.
Might be that the files need to be modified if the deliverable is different
