#!/usr/bin/env bash

#NOTE: I comment everything because I have to do this manually with the changes mentioned in https://app.clickup.com/t/34aghxe . I could  put all the changed commands in a bash file again, but I want to do it with Github actions and cloudformation so bash+cdk not interesting at.

# npm install -g aws-cdk@2.8.0
# python3 -m venv .venv
# source .venv/bin/activate
# pip3 install -r requirements.txt


# ACCOUNT_ID=$(aws sts get-caller-identity --query Account | tr -d '"')
# AWS_REGION=$(aws configure get region)
# cdk bootstrap aws://${ACCOUNT_ID}/${AWS_REGION}
# cdk deploy --parameters ProjectName=mlflow --require-approval never