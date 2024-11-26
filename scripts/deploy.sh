#!/bin/bash

cd ..

set -a
source prod.env
set +a

export NCLOUD_ACCESS_KEY=ncp_iam_BPAMKR3ymzryX8dUtHrP
export NCLOUD_SECRET_KEY=ncp_iam_BPKMKRZDUzp5M16sdMxG8UaL2MEXhYGsb3
export NCLOUD_API_GW=https://ncloud.apigw.ntruss.com

docker login stop.kr.ncr.ntruss.com -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

docker build --platform linux/amd64 -t stop.kr.ncr.ntruss.com/oz-collabo-repo:latest .
docker tag stop.kr.ncr.ntruss.com/oz-collabo-repo stop.kr.ncr.ntruss.com/oz-collabo-repo:latest

docker push stop.kr.ncr.ntruss.com/oz-collabo-repo

cd kubernetes
ncp-iam-authenticator create-kubeconfig --region KR --clusterUuid d3c299b3-a6ca-4db8-9c5e-d0138a4d6e3d --output kubeconfig.yaml

KUBECONFIG_PATH=$(realpath kubeconfig.yaml)
export KUBECONFIG=$KUBECONFIG_PATH
kubectl create secret docker-registry amuguna \
  --docker-server=stop.kr.ncr.ntruss.com \
  --docker-username=$DOCKER_USERNAME \
  --docker-password=$DOCKER_PASSWORD \
  --docker-email=$DOCKER_EMAIL


kubectl apply -f django_deployment.yaml

kubectl rollout restart deployment django-deployment

cd ..