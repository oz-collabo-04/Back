cd ..

docker login stop.kr.ncr.ntruss.com

docker build --platform linux/amd64 -t stop.kr.ncr.ntruss.com/oz-collabo-repo:latest .

export NCLOUD_ACCESS_KEY=ncp_iam_BPAMKR3ymzryX8dUtHrP

export NCLOUD_SECRET_KEY=ncp_iam_BPKMKRZDUzp5M16sdMxG8UaL2MEXhYGsb3

export NCLOUD_API_GW=https://ncloud.apigw.ntruss.com

export KUBECONFIG="/Users/mac/Desktop/oz_collabo_project/kubeconfig.yaml"

docker tag stop.kr.ncr.ntruss.com/oz-collabo-repo stop.kr.ncr.ntruss.com/oz-collabo-repo:latest

docker push stop.kr.ncr.ntruss.com/oz-collabo-repo

kubectl create secret docker-registry regcred \
--docker-server=stop.kr.ncr.ntruss.com \
--docker-username=ncp_iam_BPAMKR3ymzryX8dUtHrP \
--docker-password='ncp_iam_BPKMKRZDUzp5M16sdMxG8UaL2MEXhYGsb3' \
--docker-email=ehdugr741@naver.com

kubectl apply -f deployment.yaml

kubectl rollout restart deployment oz-collabo-deployment