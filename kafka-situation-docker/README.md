# Kafka Situation Cluster

[![Kafka](https://img.shields.io/badge/streaming_platform-kafka-black.svg?style=flat-square)](https://kafka.apache.org)
[![Docker Images](https://img.shields.io/badge/docker_images-confluent-orange.svg?style=flat-square)](https://github.com/confluentinc/cp-docker-images)
[![Python](https://img.shields.io/badge/python-3.5+-blue.svg?style=flat-square)](https://www.python.org)


## Install

You will need [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/) to run it.

You simply need to create a Docker network called `kafka-network` to enable communication between the Kafka cluster and the apps:

```bash
$ docker network create kafka-network
```


## Quickstart

- Spin up the local single-node Kafka cluster (will run in the background):

```bash
$ docker-compose -f docker-compose.kafka.yml up -d
```

- Check the cluster is up and running (wait for "started" to show up):

```bash
$ docker-compose -f docker-compose.kafka.yml logs -f broker | grep "started"
```

- Start the server 
```bash
usage: docker-compose run detector [-h] -o output_file -thr threshold -gap time gap

optional arguments:
  -h, --help      show this help message and exit
  -o output_file  path to output
  -thr threshold  threshold
  -gap time gap   time gap
  
$ docker-compose run detector -o /data/OUEPUT_DIR -thr threshold -gap time gap
```
for example

```bash 
$ docker-compose run detector -o /data/out2.json -thr 0.6 -gap 2
```

I have also written an example for how to pass the data to the server.
```bash 
$  docker-compose run generator
```
To run it. More detail please look at generator/app.py 

To stop the Kafka cluster (use `down`  instead to also remove contents of the topics):

```bash
$ docker-compose -f docker-compose.kafka.yml stop
```

To remove the Docker network:

```bash
$ docker network rm kafka-network
```
