# Director Deployment

This is an example of how to deploy a Sandgarden director pool
into your private infrastructure.

It assumes you have a private VPC already set up where your director pool will live.

## Inputs

Required:
* `namespace` - Unique identifier for your deployment (e.g., "sandgarden-poc")
* `vpc_id` - ID of your existing VPC where resources will be deployed
* `sand_api_key` - Your Sandgarden API key for director authentication

Optional:
* `tags` - Map of tags to apply to all resources (default: `{ app = "sandgarden", role = "director" }`)
* `aws_region` - AWS region for deployment (default: "us-west-2")

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars

# Set the variables as needed
# namespace="sandgarden-poc or YOUR NAMESPACE HERE"
# vpc_id="YOUR VPC ID HERE"
# tags={ app = "sandgarden", role = "director" }
# sand_api_key="YOUR API KEY HERE"
# public_subnet_cidr = "10.0.1.0/24"  # Adjust based on your VPC CIDR
# private_subnet_cidr = "10.0.2.0/24"  # Adjust based on your VPC CIDR

tofu init
tofu apply
```

## Outputs

* `lambda_role_arn` - ARN of the IAM role created for Lambda functions to use
* `ecr_registry_url` - URL of the ECR repository where container images are stored

## Resources Created

This Terraform configuration creates the following AWS resources:

Network Resources:
* Network Load Balancer in public subnets
* VPC Endpoints for ECR, CloudWatch Logs, and Secrets Manager
* Security groups for NLB and ECS tasks

Container Resources:
* ECS Fargate cluster
* ECS task definition and service
* ECR repository with pull-through cache
* CloudWatch log group for container logs

IAM Resources:
* ECS task execution role
* ECS task role
* Lambda execution role

Other:
* Secrets Manager secret for API key
* SSM Parameter for ECR repository URL


