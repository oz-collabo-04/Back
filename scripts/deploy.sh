#!/bin/bash

cd ..

set -a
source prod.env
set +a

docker login stop.kr.ncr.ntruss.com -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

docker build --platform linux/amd64 -t stop.kr.ncr.ntruss.com/oz-collabo-repo:latest .
docker tag stop.kr.ncr.ntruss.com/oz-collabo-repo stop.kr.ncr.ntruss.com/oz-collabo-repo:latest

docker push stop.kr.ncr.ntruss.com/oz-collabo-repo

kubectl create secret docker-registry regcred \
  --docker-server=stop.kr.ncr.ntruss.com \
  --docker-username=$DOCKER_USERNAME \
  --docker-password=$DOCKER_PASSWORD \
  --docker-email=$DOCKER_EMAIL

kubectl apply -f deployment.yaml

kubectl rollout restart deployment oz-collabo-deployment
