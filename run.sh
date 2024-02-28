#!/usr/bin/env bash

docker stop $(docker ps -a -q)
docker container prune
docker build  -t keystone-api:local .
docker run -p 8000:8000 --name keystone-local keystone-api:local
