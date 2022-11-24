# mlops-covid
My capstone project for the MLOps Zoomcamp
The project consists on implementing the MLOps environment for a COVID Predictor. Examples of predictions are:
- Predict the cases for today for a given location
- Predict the cases for following days for the whole world.
- ...

# Problem description
- The goal will be predicting the cumulative number of confirmed COVID19 cases in various locations across the world, as well as the number of resulting fatalities, for future dates. 
- The input data is available here rom the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE).
- The problem is inspired by the Kaggle competition https://www.kaggle.com/competitions/covid19-global-forecasting-week-2

Note: There is a README.md file in each folder with instructions.

# Solution description for V1: 
- Experiment tracking and model registry:
    - Experiment tracking with MLflow: several items will be tracked:
        - Parameters used in the models like the maximal degree of the polynomial features, ...
        - Metric: the main metric will be root mean squared logarithmic error (RMSLE)
        - Artifacts: here mainly we will work with pickled models for the different models tested
        - Source will not be tracked
    - Model management and Model registry with MLflow:  for model versioning, stage transitions,... and mainly to have a model in production that will be used in the pipeline

- Workflow orchestration
    - The workflow will be orchestrated using Prefect

- Model monitoring
    - The model monitoring will consist in the supervision of the RMSLE also with Prefect

For more details see the section below "Explanation of the folders and files in order"

# Prerequisite 
You need to have installed aws cli in your machine. See [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for more details.

# Init
```
/mlops-covid$ pip install pipenv && pipenv install --dev
```

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
10) Github actions in workflows. CI implemented in .github/workflows/ci-tests.yml for the setup, installing, testing, linting... For the Github actions to work you need to set the corresponding Secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PREFECT_API_KEY, PREFECT_WS and PREFECT_S3BLOCK_NAME. CD not implemented since atm there is no Docker nor Terraform.

# Reproduce
You can choose to reproduce all the steps of the process following the READMEs on the previously mentioned folders or just focus on the folder /delivery for the end result.

# Github Versions for different Versions of the project
- Project V1 - CU Task: 2u9yn99 - Github sha: 3a7197265fad1212399b61dac5219e5cf5a84874
- Project V2 - CU Task: 34aghxe - Github sha: TBD

