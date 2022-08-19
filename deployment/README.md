# Script Deployment

deployment/inbetween_nb.ipynb is an in-between notebook that it will be converted to a python script.

The python script generated from this notebook /deployment/inbetween_nb.py.
Prefect is used in this script to make a workflow.
Example to call this script: 
```bash 
...deployment$ python inbetween_nb.py Madrid 16082a31f2be4eadb6f368b4ded2d309
```

# Prefect

The script deployment/covid_pred_deploy.py is for the deployment of the Prefect flow. 

Install the Prefect version 0b16 
```bash 
pip install prefect==2.0b16
```
cause everything gives problems
To see the Prefect UI enter in the terminal 
```bash
prefect orion start
```
 and then go to http://127.0.0.1:4200/

```bash 
prefect deployment build ./inbetween_nb.py:covid_prediction -n CovidPredictor_3 -t tag_CovidPrev_3
```
Now in the same folder a manifest and a yaml file are automatically created
Modify the deployment.yaml to add the necessary parameters:
```yaml
parameters: {
    "Prov_St": "Madrid",
    "run_id": "16082a31f2be4eadb6f368b4ded2d309",
}
```

```bash
prefect deployment apply deployment.yaml
```
Now the Deployment appears under http://127.0.0.1:4200/deployments

In the Prefect UI now one can create a work queue to test it. Under Deployments (Optional) select CovPredictor. And with the ID of this work queue then start an agent entering in the terminal: 

```bash
prefect agent start <WorkQueue ID>
```

In the Prefect UI under Deployments click on CovPredictor and run it.

If you want to schedule it:
Create another deployment file like deployment/scheduled_deployment.yaml and edit the scheduler like here:
schedule:
  cron: 53 10 * * *
  timezone: Europe/Berlin

Note: if it does not work you might need to start from the beginning doing something like 
```bash
prefect deployment build ./inbetween_nb.py:covid_prediction -n CovidPredSched -t tag_CovidPrevSched
```

Make sure all your other work queues are stopped. 


Then apply this new deployment file to prefect as before 
```bash
prefect deployment apply scheduled_deployment.yaml
```
Create a new work queue and start the corresponding agent in the terminal 
```bash
prefect agent start <WorkQueue ID>
```

