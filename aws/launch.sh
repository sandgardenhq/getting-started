#!/bin/bash

set -e

cd /home/ec2-user

# This shortcut just makes it easier to debug later if you want local access
ln -fs /var/lib/cloud/instance/user-data.txt ./launch.sh
chmod +x launch.sh

dnf install -y docker
systemctl enable docker
systemctl start docker

# TODO: This is a hack to get the director to boot without restarting since we don't have systemd configured yet
mkdir -p /home/ec2-user/.sandgarden
echo '{"restarted":true}' > /home/ec2-user/.sandgarden/staticcfg.json

# Fetch the VERSION from SSM Parameter Store
VERSION=$(aws ssm get-parameter --name "/${namespace}/director/version" --query "Parameter.Value" --output text)
BUCKET=$(aws ssm get-parameter --name "/${namespace}/director/binaries_bucket_name" --query "Parameter.Value" --output text)

aws s3 cp s3://$${BUCKET}/sgdirector/$${VERSION}/sgdirector_linux_amd64 sgdirector
chmod +x sgdirector

aws secretsmanager get-secret-value --secret-id ${secrets_name} --query SecretString --output text > secrets.json

echo "SAND_NAMESPACE=${namespace}" > .env.director
echo "SAND_LOG_LEVEL=debug" >> .env.director
echo "SAND_DIRECTOR_LISTEN_ADDRESS=0.0.0.0:8443" >> .env.director
echo "SAND_ECR_REPO=${ecr_repo}" >> .env.director
echo "SAND_ECR_REGISTRY=${ecr_registry}" >> .env.director

echo "AWS_REGION=${aws_region}" >> .env.director
echo "HOME=/home/ec2-user" >> .env.director

SAND_API_KEY=$(jq -r '.SAND_API_KEY' secrets.json)
echo "SAND_API_KEY=$${SAND_API_KEY}" >> .env.director

set -a # automatically export all variables
source .env.director
set +a

echo "Starting director $${VERSION}..."

nohup /home/ec2-user/sgdirector serve >> /home/ec2-user/sgdirector.log 2>&1 &
