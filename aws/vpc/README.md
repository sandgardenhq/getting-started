# Director Deployment in AWS VPC

This guide demonstrates how to deploy a Sandgarden director pool into your private AWS infrastructure. The deployment:
- Creates a highly available director pool
- Configures secure network access
- Sets up monitoring and logging

## Prerequisites
- Existing AWS VPC
- AWS CLI configured with appropriate permissions
- Terraform or OpenTofu installed locally

## Inputs

Required:
* `namespace` - Unique identifier for your deployment (e.g., "sandgarden-poc")
* `vpc_id` - ID of your existing VPC where resources will be deployed
* `sand_api_key` - Your Sandgarden API key for director authentication

Optional:
* `tags` - Map of tags to apply to all resources (default: `{ app = "sandgarden", role = "director" }`)
* `aws_region` - AWS region for deployment (default: "us-west-2")

## Usage

1. Copy the example variables file and edit it with your specific values.

```bash
cp terraform.tfvars.example terraform.tfvars
```

```hcl 
namespace = "sandgarden-poc"              # Your unique identifier
vpc_id    = "vpc-1234567890abcdef0"      # Your VPC ID
tags      = {
  app  = "sandgarden"
  role = "director"
}
sand_api_key = "your_api_key_here"

# Network Configuration
public_subnet_cidr  = "10.0.1.0/24"      # Must be within VPC CIDR
private_subnet_cidr = "10.0.2.0/24"      # Must be within VPC CIDR
```

2. Initialize Terraform and apply the configuration.

```bash
tofu init
tofu apply
```

## Outputs

* `ecr_registry_url` - URL of the ECR repository where container images are stored

## Resources Created

This Terraform configuration creates the following AWS resources:

Network Resources:
* Network Load Balancer in public subnets
* VPC Endpoints for ECR, CloudWatch Logs, and Secrets Manager
* Security groups for NLB and ECS tasks

Container Resources:
* ECS EC2 cluster
* ECS task definition and service
* ECR repository with pull-through cache
* CloudWatch log group for container logs

IAM Resources:
* ECS task execution role
* ECS task role

Other:
* Secrets Manager secret for API key
* SSM Parameter for ECR repository URL


