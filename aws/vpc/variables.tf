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

variable "task_cpu" {
  description = "ECS Task instance CPU units (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "ECS Task instance memory in MiB"
  type        = number
  default     = 970
}

variable "director_version" {
  description = "Version of the Sandgarden Director image to use. If not specified, latest tag will be used."
  type        = string
  default     = "latest"
}

variable "cluster_name" {
  description = "Cluster name for created directors"
  type        = string 
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
}

variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
}

