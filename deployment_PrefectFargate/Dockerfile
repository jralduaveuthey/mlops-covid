FROM prefecthq/prefect:2-python3.9
RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /opt/prefect
COPY setup.py .
COPY requirements.txt .
RUN pip install .
RUN prefect block register -m prefect_aws.ecs
