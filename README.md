# mlops-covid
My capstone project for the MLOps Zoomcamp

Note: There is a README.md file in each folder with instructions.


# Init
/mlops-covid$ pip install pipenv && pipenv install --dev

# Explanation of the folders and files in order
1) /EDA: here some basic EDA takes place on the covid dataset
2) /exp-track-mod-reg: working with the Experiment tracking and Model Registry in MLflow. A Model is selected for the deployment. Different strategies are considered for deployment
3) /deployment: basic deployment of the model in a batch mode scheduled with Prefect running the Agent Locally
4) /deployment_PrefectRemoteAgent: deployment of the model in a batch mode scheduled with Prefect running the Agent remotely in a EC2 instance started manually
5) /monitoring: added monitoring via another Prefect flow that stores monitored metric in S3 bucket
6) /deployment+monitoring: putting together the both Prefect flows (prediction done in deployment_PrefectRemoteAgent and monitoring flow)
7) /testing: unit test, linting and formating to get a code
8) File .pre-commit-config.yaml with pre-commit hooks for testing, linting and formating
9) Makefile that runs some checks and moves file folder that can be delivered. Instructions on how to have it running are added manually in the README.md

# Reproduce
You can choose to reproduce all the steps of the process following the READMEs on the previously mentioned folders or just focus on the folder /delivery for the end result.
