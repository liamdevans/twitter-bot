FROM python:3.8

RUN apt-get update && apt-get install -y git

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME
COPY dagster.yaml $DAGSTER_HOME

COPY twitter_bot/* /twitter_bot/
COPY configs/* /twitter_bot/configs/
COPY requirements.txt /tmp

RUN pip3 install -r /tmp/requirements.txt

WORKDIR /twitter_bot

# Run dagster gRPC server on port 4000
EXPOSE 4000

CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "main.py"]
#CMD ["dagster-daemon", "run"]
