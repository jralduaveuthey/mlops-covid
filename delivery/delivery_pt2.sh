#!/usr/bin/env bash
cd delivery/
echo "Login in in Prefect Cloud"
prefect cloud login -k $PREFECT_API_KEY
prefect cloud workspace set --workspace $PREFECT_WS
echo "Create Prefect Deployment"
prefect deployment build ./covid_PredMonitor.py:monitor -n CovidPredMonitor -t tag_CovidPredMonitor --storage-block s3/$PREFECT_S3BLOCK_NAME
FILE='./deployment.yaml'
if [ -e "$FILE" ]; then
    echo "File $FILE exists."
    file_temp=$FILE
    deployment_prefix='covid-prediction'
else
    echo "File $FILE does not exist."
    file_temp='./monitor-deployment.yaml'
    deployment_prefix='monitor'
fi
example_parameters='parameters: { "run_id": "16082a31f2be4eadb6f368b4ded2d309"}'
sed -i "s/^parameters: {}/${example_parameters}/" $file_temp
mv $file_temp monitoring.yaml
prefect deployment apply monitoring.yaml
echo "Run Prefect Deployment..."
prefect deployment run $deployment_prefix/CovidPredMonitor
echo "Starting Prefect Agent..."
prefect agent start -t tag_CovidPredMonitor
echo "Please run delivery_pt2.sh in another terminal to continue..."
