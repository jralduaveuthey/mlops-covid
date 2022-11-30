# Goal of this folder
The goal is to have the same set up (scheduled batch) as in the folder deployment/ but running in on the cloud.
For that here I will use a Prefect Agent on a container on AWS ECS Fargate.
A scheduled Deployment in the Prefect Cloud will communicate with the Prefect Agent on the container on AWS.

# Python Script 
Here the script deployment_docker/covid_pred.py is a copy of deployment/inbetween_nb.py. Same applies to the files deployment.yaml and covid_prediction-manifest.json.


# Prefect Cloud
To run the Deployments I will use the Prefect Cloud following the instructions here: https://docs.prefect.io/ui/cloud-getting-started/
To know more in detail check the folder deployment_PrefectDockerAgent/cloud-getting-started

# Login in Cloud and set workspace
Login in the Prefect Cloud in the terminal with:
```
prefect cloud login -k <API_KEY>
```
To sync a local execution environment with the workspace prefect cloud workspace run in the cli:
```
prefect cloud workspace set --workspace "jaimerv/workinonit"
```
"jaimerv/workinonit" is the name of my workspace in my Prefect Cloud account, so you will need to pass here the name of the workspace you created in your account.


# Deploy Infrastructure
Before running the Github action (called "DEPLOY ECS Cluster, Prefect agent ECS service and ECR repository") on the browser, you have to enter some Github Secrets and Inputs for the action to work.

## Github necessary secrets 
- AWS_ACCESS_KEY_ID: You can see how to obtain one [here.](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
- AWS_SECRET_ACCESS_KEY: You can see how to obtain one [here.](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
- PREFECT_API_KEY: You can see more detailed info [here.](https://docs.prefect.io/ui/cloud-getting-started/#create-an-api-key)
- PREFECT_API_URL: You can see more detailed info [here.](https://docs.prefect.io/ui/cloud-getting-started/#create-an-api-key)


## Inputs for the Deployment Github action
The inputs for the Github action are the following:
- cpu: CPU for the agent. The default is '512' but you can choose between the following ['256', '512', '1024', '2048', '4096']
- memory: Memory for the agent. The default is '1024' but you can choose between the following ['512', '1024', '2048', '4096', '5120', '6144', '7168', '8192']
- project_id: Unique ID of your project that will be used for the name of the Prefect blocks, ...
- aws-region: the AWS Region where your resources will be deployed
- prefect-version: Prefect version to use for flows. Default version is '2.6.9' but it should work with any 2.* Prefect version
- prov_st: City where you want to predict the covid cases
- run_id: run_id from the model to use in the S3 bucket mlflow-artifacts-remote-jaime/4/. This is my 
- cron_sch: Cron schedule to use in the deployment
- timezone: Timezone to use in the cron schedule 

## Jobs for the Deployment
1. **Create S3 Bucket**: Creates the S3 Bucket where and all the files in this folder will be copied to the bucket. 

2. **ECR Repo & Image**: Creates a new ECR repository using the AWS CloudFormation under _deployment_PrefectFargate\infrastructure\ecr_repository.yml_. Then it logs in to our Amazon ECR and builds, tags, and pushes an image to this ECR based on the file _deployment_PrefectFargate\Dockerfile_.

3. **ECS Cluster & Prefect Agent**: Adds Prefect Cloud Secrets to SSM Parameter Store (needed for container in ECS task): PREFECT_API_URL + PREFECT_API_KEY. Then deploys to ECS with the AWS CloudFormation template _deployment_PrefectFargate/infrastructure/ecs_cluster_prefect_agent.yml_. Then generates a task definition and uploads it as artifact so are able to see it in the Github page after the action is finished.

4. **Prefect Blocks & S3 Upload**: Creates the Prefect Blocks for AWS Credentials and S3. Creates ECS Task with the image that was pushed in the previous step. For the deployment the schedule given in the Github action inputs (cron + timezone) will be used.
Then it creates a deployment definition (yaml) file, that will be updloaded to the S3 bucket created in the first step, and used by the Prefect Agent to run your flow.

## See the results in the Prefect Cloud
In your browser you can go to the [Prefect Cloud](https://app.prefect.cloud/) and see your new Flow Runs, Blocks, Work Queue, ... For the Flow Runs you can also see the Logs that were defined in _deployment_PrefectFargate\covid_pred.py_. More info about the Prefect Cloud and how to operate with it can be found [here.](https://docs.prefect.io/ui/overview/)


# Continued Deployment
If you wish to make any changes you do not have to deploy everything again, it is enough with running the Github action called **CD** (see code under _.github\workflows\CD.yml_).  

Possible changes that you might wish to do include:
- Changes in your python code (in this case _deployment_PrefectFargate\covid_pred.py_).
- Changes in the scheduling of your function (via cron Github input in action).
- A different run_id for a different ML model to use in production.
- Different S3 buckets
- ...


At the moment the Github action is defined to be triggered on workflow_dispatch so it is easier to play with it but to use it as real CD pipeline one would only have to stop passing the parameters as Github action inputs and change the trigger. For more detailed information see [here.](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#available-events)


# Destroy AWS Resources
>>>>TODO







## Run a flow from a deployment getting the flow code from remote storage in S3 bucket 
### Register a S3 Block
Create a S3 Block in Prefect Cloud(like done here: https://discourse.prefect.io/t/how-to-deploy-prefect-2-0-flows-to-aws/1252/5)
This S3 Block has as a S3 location the bucket: "prefect-cloud-flow-codes/covid_predictor"

### Create a flow script 
The following command creates the json file and the yaml file locally and under the s3 bucket
```
cd deployment_PrefectRemoteAgent/
prefect deployment build ./covid_pred.py:covid_prediction -n CovidPrev_EC2 -t tag_CovidPrev_EC2 --storage-block s3/covid-predictor
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
This will create a Deployment to run on a Schedule “At 12:20.” every day.

### Create the deployment using the Prefect CLI
```
prefect deployment apply deployment.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the python script file in the S3 bucket.

### Create a flow run for the given flow and deployment (if not scheduled)
```
prefect deployment run covid-prediction/CovidPrev_EC2
```

## Configure the EC2 instance [DELETEME]
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
prefect agent start -t tag_CovidPrev_EC2
```