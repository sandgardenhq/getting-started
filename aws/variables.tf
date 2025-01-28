variable "namespace" {
  description = "Namespace for resource naming"
  type        = string
  default     = "sandgarden"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {
    Project = "sandgarden"
  }
}

variable "vpc_id" {
  description = "VPC ID where resources will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the ECS service"
  type        = list(string)
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-2"  # Adjust default as needed
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "sandgarden"
}

variable "sand_api_key" {
  description = "Sandgarden API key"
  type        = string
}

variable "sandgarden_ecr_repo_url" {
  description = "URL of the ECR repository containing the Sandgarden Director image"
  type        = string
  default     = "public.ecr.aws"  # Changed to just the registry domain
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 1024
}

variable "fargate_memory" {
  description = "Fargate instance memory in MiB"
  type        = number
  default     = 2048
}

