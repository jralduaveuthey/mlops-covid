# Experiment tracking and model registry with MLflow server on Fargate

To start the MLflow Tracking Server you need to start the Github action "(V2) Deploy MLFlow Service Infrastructure". The URI of the MLflow server is on the corresponding Load Balancer in AWS, and it is also an output of the cf-stack.  

Once you have the infrastructure deploy you can use this URI in the notebooks in the folder exp-track-mod-reg-mlflowFargate.  

To delete the mlflow infrastructure you need to start the Github action "(V2) Delete MLFlow Service Infrastructure".  

To follow the Experiment Tracking part in mlflow follow the steps in the notebook exp-track-mod-reg-mlflowFargate\exp-track.ipynb in this folder.  

In the notebook exp-track-mod-reg-mlflowFargate\model-registry.ipynb I explain the process followed for model registry and model selection
