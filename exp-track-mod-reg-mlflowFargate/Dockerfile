ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION} AS foundation

RUN apt-get update && \
  apt-get install -y build-essential curl wget cmake && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

RUN mkdir -p /opt/experiment-tracking/repo

COPY pyproject.toml poetry.toml poetry.lock /opt/experiment-tracking/repo/

WORKDIR /opt/experiment-tracking/repo

RUN curl -sSL https://install.python-poetry.org | python3 - && \
  export PATH=$PATH:$HOME/.local/bin && \
  poetry --version && \
  poetry install --no-dev

# RUN pip install \
#     mlflow \
#     pymysql \
#     boto3 & \

RUN mkdir /mlflow/

FROM python:${PYTHON_VERSION}-slim
COPY --from=foundation /opt/experiment-tracking/repo /opt/experiment-tracking/repo
ENV PATH=/opt/experiment-tracking/repo/.venv/bin:$PATH

ENV PYTHONUNBUFFERED 1
WORKDIR /opt/experiment-tracking/repo

EXPOSE 5000

## Environment variables made available through the Fargate task.
## Do not enter values
CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --default-artifact-root ${MLFLOW_ARTIFACT_URI} \
    --backend-store-uri mysql+pymysql://${MLFLOW_DB_USERNAME}:${MLFLOW_DB_PASSWORD}@${MLFLOW_DB_HOST}:${MLFLOW_DB_PORT}/${MLFLOW_DB_DATABASE}


# CMD ["mlflow", "server", "--host" "0.0.0.0", "--port", "5000", "fastapi_app:app"]
