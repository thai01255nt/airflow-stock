ARG PYTHON_VERSION=3.8.0
FROM python:$PYTHON_VERSION

ENV BASE_DIR=airflow-stock

RUN echo "Installing system deps" \
    && apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y python3-venv \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip setuptools

# Setup workdir
RUN mkdir $BASE_DIR
WORKDIR $BASE_DIR

# Setup
RUN echo "Copy setup file to $BASE_DIR"
RUN ls
COPY ./setup.sh ./setup.sh
COPY ./requirements.txt ./requirements.txt
RUN ls
RUN chmod +x setup.sh && ./setup.sh

ADD ./ ./
COPY ./dags ./pwd/dags
RUN ls ./pwd
# Run server
RUN chmod +x run.sh
CMD ["./run.sh"]
