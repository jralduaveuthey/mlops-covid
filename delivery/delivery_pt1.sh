#!/usr/bin/env bash
cd delivery/
echo "Deleting unnecessary files..."
ls | grep -v "delivery_pt1.sh\|delivery_pt2.sh\|covid_PredMonitor.py\|README.md" | xargs rm -rf #delete all files in folder but these two files and README.md
echo "Login in in Prefect Cloud..."
prefect cloud login -k $PREFECT_API_KEY
prefect cloud workspace set --workspace $PREFECT_WS
echo "Create Prefect Deployment..."
prefect deployment build ./covid_PredMonitor.py:covid_prediction -n CovidPredictor -t tag_CovidPredictor --storage-block s3/$PREFECT_S3BLOCK_NAME
FILE='./deployment.yaml'
if [ -e "$FILE" ]; then
    echo "File $FILE exists."
    file_temp=$FILE
    deployment_prefix='covid-prediction'
else
    echo "File $FILE does not exist."
    file_temp='./covid_prediction-deployment.yaml'
    deployment_prefix='covid_prediction'
fi
example_parameters='parameters: { "Prov_St": "Berlin", "run_id": "16082a31f2be4eadb6f368b4ded2d309"}'
sed -i "s/^parameters: {}/${example_parameters}/" $file_temp
mv $file_temp predicting.yaml
prefect deployment apply predicting.yaml
echo "Run Prefect Deployment..."
prefect deployment run covid-prediction/CovidPredictor
echo "Starting Prefect Agent..."
prefect agent start -t tag_CovidPredictor
echo "Please run delivery_pt2.sh in another terminal to continue..."
