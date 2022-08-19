# Goal of this folder
Here I am to join the flows for the batch prediction process and the monitoring in one script.
Also here I will apply best practices like:
- unit tests
- integration test
- Linter and/or code formatter
- Makefile
- pre-commit hooks

# Python Script 
Here I combine the flow from /deployment_PrefectRemoteAgent/covid_pred.py and the flow from/monitoring/covid_pred_monitor.py

# Prefect Cloud
To run the Deployments I will use the Prefect Cloud following the instructions here: https://docs.prefect.io/ui/cloud-getting-started/
To know more in detail check the folder /deployment_PrefectDockerAgent/cloud-getting-started

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

## Register a S3 Block
Create a S3 Block in Prefect Cloud(like done here: https://discourse.prefect.io/t/how-to-deploy-prefect-2-0-flows-to-aws/1252/5)
This S3 Block has as a S3 location the bucket: "prefect-cloud-flow-codes/covid_predictor"

# PREDICTION batch pipeline

### Create a flow script for PREDICTIONS
The following command creates the json file and the yaml file locally and under the s3 bucket
```
cd deployment+monitoring/
prefect deployment build ./covid_pred+monitor.py:covid_prediction -n CovidPred -t tag_CovidPred --storage-block s3/covid-predictor
```
After running this command the deployment.yaml will contain "storage:  bucket_path: prefect-cloud-flow-codes/basic_flow". That means that the manifest json file and the python script with the code will be retrieved from this S3 bucket when creating the Deployment and everytime the Deployment runs. At this point one can delete the json manifest and the python script with the flow from the local folder since they will not be used (although Prefect creates them both locally and in the bucket)

Modify the deployment.yaml to add the necessary parameters. For example:
```
schedule:
  cron: 20 12 * * *
  timezone: Europe/Berlin
parameters: {
    "Prov_St": "Madrid",
    "run_id": "16082a31f2be4eadb6f368b4ded2d309",
}
```

### Rename /deployment+monitoring/deployment.yaml to /deployment+monitoring/predicting.yaml
This is not strictly necessary but helps to differentiate between the yaml for Predicting and the yaml for monitoring

### Create the deployment using the Prefect CLI
```
prefect deployment apply predicting.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the python script file in the S3 bucket.

### Create a flow run for the given flow and deployment (if not scheduled)
```
prefect deployment run covid-prediction/CovidPred
```

## Configure the EC2 instance
To have an Agent in an EC2 instance as your execution layer follow the steps here https://discourse.prefect.io/t/how-to-deploy-a-prefect-2-0-agent-to-an-ec2-instance-as-your-execution-layer/551

At the moment automating this part via Terraform only works for Prefect 1.0 https://discourse.prefect.io/t/announcing-the-terraform-module-to-deploy-the-prefect-docker-agent-on-aws-ec2/584 so this part unfortunately must be done manually. 

### Configue a work queue that can allocate your deployment's flow runs to agents AND Start an agent in your execution environment
In the new created EC2 machine login into your Prefect Cloud

```
prefect cloud login -k <API_KEY>
prefect cloud workspace set --workspace "jaimerv/workinonit"
```

and run:

```
prefect agent start -t tag_CovidPred
```




# MONITORING batch pipeline


### Create a flow script for PREDICTIONS
The following command creates the json file and the yaml file locally and under the s3 bucket
```
cd deployment+monitoring/
prefect deployment build ./covid_pred+monitor.py:monitor -n CovidPredMonitor -t tag_CovidPredMonitor --storage-block s3/covid-predictor
```
After running this command the deployment.yaml will contain "storage:  bucket_path: prefect-cloud-flow-codes/basic_flow". That means that the manifest json file and the python script with the code will be retrieved from this S3 bucket when creating the Deployment and everytime the Deployment runs. At this point one can delete the json manifest and the python script with the flow from the local folder since they will not be used (although Prefect creates them both locally and in the bucket)

Modify the deployment.yaml to add the necessary parameters. For example:
```
schedule:
  cron: 15 16 * * *
  timezone: Europe/Berlin
parameters: {
    "run_id": "16082a31f2be4eadb6f368b4ded2d309",
}
```

### Rename /deployment+monitoring/deployment.yaml to /deployment+monitoring/monitoring.yaml
This is not strictly necessary but helps to differentiate between the yaml for Predicting and the yaml for monitoring

### Create the deployment using the Prefect CLI
```
prefect deployment apply monitoring.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the python script file in the S3 bucket.

### Create a flow run for the given flow and deployment (if not scheduled)
```
prefect deployment run monitor/CovidPredMonitor
```

## Configure the EC2 instance
To have an Agent in an EC2 instance as your execution layer follow the steps here https://discourse.prefect.io/t/how-to-deploy-a-prefect-2-0-agent-to-an-ec2-instance-as-your-execution-layer/551

At the moment automating this part via Terraform only works for Prefect 1.0 https://discourse.prefect.io/t/announcing-the-terraform-module-to-deploy-the-prefect-docker-agent-on-aws-ec2/584 so this part unfortunately must be done manually. 

### Configue a work queue that can allocate your deployment's flow runs to agents AND Start an agent in your execution environment
In the new created EC2 machine login into your Prefect Cloud

```
prefect cloud login -k <API_KEY>
prefect cloud workspace set --workspace "jaimerv/workinonit"
```

and run:

```
prefect agent start -t tag_CovidPredMonitor
```

# Testing
See under /deployment+monitoring/code
The file with the flows had to be renamed to covid_PredMonitor.py because pytest complained of the previous name.