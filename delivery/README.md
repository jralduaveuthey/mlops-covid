Here the instructions to run the code in this folder.
For simplification I will run the Prefect Agent locally but to do it remotely on a EC2 machine follow the instructions in /deployment_PrefectRemoteAgent/README.md
The Prefect Deployments will be in the Prefect Cloud and the storage of the Deployments and the results from the flows (predictions and monitored metrics) will be stored in a S3 bucket.

# Prefect Cloud
To run the Deployments use the Prefect Cloud following (more in depth instructions can be found here: https://docs.prefect.io/ui/cloud-getting-started/)
You can see the UI under https://app.prefect.cloud/

## Create a S3 bucket in AWS and Register a S3 Block
Create a S3 bucket in AWS. The one I use for this example is called "prefect-cloud-flow-codes/covid_predictor" but replace this with your own bucket name.
Create a S3 Block in Prefect Cloud(like done here: https://discourse.prefect.io/t/how-to-deploy-prefect-2-0-flows-to-aws/1252/5)
This S3 Block has as a S3 location my S3 bucket: "prefect-cloud-flow-codes/covid_predictor"

NOTE: You can choose to do the following steps manually to understand better the process or just run delivery_pt1.sh and delivery_pt2.sh in different terminals. This will deploy and run non-scheduled flows.
If you choose to run the *.sh files make sure you have the following environmental variables in your terminals:

```
export PREFECT_API_KEY=<API_KEY>
export PREFECT_WS=<your workspace> # jaimerv/workinonit
export PREFECT_S3BLOCK_NAME=<your S3 block here> # covid-predictor
bash delivery_pt1.sh
```

and also in the secodn terminal:
```
export PREFECT_API_KEY=<API_KEY>
export PREFECT_WS=<your workspace> # jaimerv/workinonit
export PREFECT_S3BLOCK_NAME=<your S3 block here> # covid-predictor
bash delivery_pt2.sh
```

## Login in Cloud and set workspace
Login in the Prefect Cloud in the terminal with:
```
prefect cloud login -k <API_KEY>
```
To sync a local execution environment with the workspace prefect cloud workspace run in the cli:
```
prefect cloud workspace set --workspace "jaimerv/workinonit"
```
"jaimerv/workinonit" is the name of my workspace in my Prefect Cloud account, so you will need to pass here the name of the workspace you created in your account.

# PREDICTION batch pipeline

## Create a flow script for PREDICTIONS
The following command creates the json file and the yaml file locally and under the S3 bucket
```
cd delivery/
prefect deployment build ./covid_PredMonitor.py:covid_prediction -n CovidPredictor -t tag_CovidPredictor --storage-block s3/covid-predictor
```
After running this command the deployment.yaml will contain "storage:  bucket_path: prefect-cloud-flow-codes/basic_flow". That means that the manifest json file and the python script with the code will be retrieved from this S3 bucket when creating the Deployment and everytime the Deployment runs. At this point one can delete the json manifest and the python script with the flow from the local folder since they will not be used (although Prefect creates them both locally and in the bucket)

Modify the deployment.yaml to add the necessary parameters. For example:
```
schedule:
  cron: 20 14 * * *
  timezone: Europe/Berlin
parameters: {
    "Prov_St": "Berlin",
    "run_id": "16082a31f2be4eadb6f368b4ded2d309",
}
```
Adapt this schedule to a nearer time so that you can see the results.

## Rename /delivery/deployment.yaml to /delivery/predicting.yaml
This is not strictly necessary but helps to differentiate between the yaml for Predicting and the yaml for monitoring

## Create the deployment using the Prefect CLI
```
prefect deployment apply predicting.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the python script file in the S3 bucket.

## Run the Agent
```
prefect agent start -t tag_CovidPredictor
```




# MONITORING batch pipeline
You can run this in a new terminal to leave the agent runnign on the first one.

## Create a flow script for PREDICTIONS
The following command creates the json file and the yaml file locally and under the s3 bucket
```
cd delivery/
prefect deployment build ./covid_PredMonitor.py:monitor -n CovidPredMonitor -t tag_CovidPredMonitor --storage-block s3/covid-predictor
```
After running this command the deployment.yaml will contain "storage:  bucket_path: prefect-cloud-flow-codes/basic_flow". That means that the manifest json file and the python script with the code will be retrieved from this S3 bucket when creating the Deployment and everytime the Deployment runs. At this point one can delete the json manifest and the python script with the flow from the local folder since they will not be used (although Prefect creates them both locally and in the bucket)

Modify the deployment.yaml to add the necessary parameters. For example:
```
schedule:
  cron: 25 14 * * *
  timezone: Europe/Berlin
parameters: {
    "run_id": "16082a31f2be4eadb6f368b4ded2d309",
}
```

## Rename /delivery/deployment.yaml to /delivery/monitoring.yaml
This is not strictly necessary but helps to differentiate between the yaml for Predicting and the yaml for monitoring

## Create the deployment using the Prefect CLI
```
prefect deployment apply monitoring.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the python script file in the S3 bucket.

## Run the Agent
```
prefect agent start -t tag_CovidPredMonitor
```
