# Goal of this folder

Here I add the files and others used when following  https://docs.prefect.io/ui/cloud-getting-started/

# Prefect Cloud
To run the Deployments I will use the Prefect Cloud following the instructions here: https://docs.prefect.io/ui/cloud-getting-started/

## Login in Cloud and set workspace
Login in the Prefect Cloud in the terminal with:
```
prefect cloud login --key <API_KEY>
```
To sync a local execution environment with the workspace prefect cloud workspace run in the cli:
```
prefect cloud workspace set --workspace "jaimerv/workinonit"
```
"jaimerv/workinonit" is the name of my workspace in my Prefect Cloud account, so you will need to pass here the name of the workspace you created in your account.

Set Storage in S3 bucket for the flow code for deployments. For that I create an S3 bucket called prefect-cloud-flow-codes.
When doing "prefect deployment build..." one must add
```
--storage-block s3/example-block
```

## Run a flow from a deployment 
Deployments are flows packaged in a way that let you run them directly from the Prefect Cloud UI, either ad-hoc runs or via a schedule.
To run a flow from a deployment with Prefect Cloud, you'll need to:

### Create a flow script
```
prefect deployment build ./basic_flow.py:basic_flow -n test-deployment -t test_deployment
```

### Create the deployment using the Prefect CLI
```
prefect deployment apply deployment.yaml
```
### Configure a work queue that can allocate your deployment's flow runs to agents AND Start an agent in your execution environment
In Prefect Cloud, you can create a work queue by selecting the Work Queues page, then creating a new work queue.
But you can also do it from the terminal:
In your terminal, run the 
```
prefect agent start -t test_deployment
```
 command, passing a -t test_deployment option that creates a work queue for test tags.

### Run your deployment to create a flow run
To start an ad-hoc flow run, select the Run button from Prefect Cloud.

------------------------------------------------------------------------------------------------

## Run a flow from a deployment getting the flow code from remote storage in S3 bucket 
### Register a S3 Block
Create a S3 Block in Prefect Cloud(like done here: https://discourse.prefect.io/t/how-to-deploy-prefect-2-0-flows-to-aws/1252/5)

### Create a flow script 
The following command creates the json file and the yaml file locally and under the s3 bucket
```
prefect deployment build ./basic_flow.py:basic_flow -n test-deployment -t test_deployment_s3 --storage-block s3/my-s3-block-prefect-cloud
```
After running this command the deployment.yaml will contain "storage:  bucket_path: prefect-cloud-flow-codes/basic_flow". That means that the manifest json file and the python script with the code will be retrieved from this S3 bucket when creating the Deployment and everytime the Deployment runs. At this point one can delete the json manifest and the python script with the flow from the local folder since they will not be used (although Prefect creates them both locally and in the bucket)

### Create the deployment using the Prefect CLI
```
prefect deployment apply deployment.yaml
```
This will create the Deployment and since in the yaml file has the S3 as the storage, every time the Deployment runs it will get the flow from the script file in the S3 bucket.

### Configure a work queue that can allocate your deployment's flow runs to agents AND Start an agent in your execution environment
```
prefect agent start -t test_deployment_s3
```