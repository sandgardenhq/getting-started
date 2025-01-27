variable "namespace" {
  description = "Namespace to prefix resources"
  type        = string
  default     = "sandgarden"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "vpc_id" {
  description = "VPC ID to deploy into"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs to deploy into"
  type        = list(string)
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-2"
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
  description = "Sandgarden ECR repository URL"
  type        = string
  default     = "public.ecr.aws/h7j2x0j6/sandgarden-director"
}

variable "fargate_cpu" {
  description = "Director Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  default     = "2048"
}

variable "fargate_memory" {
  description = "Director Fargate instance memory to provision (in MiB)"
  default     = "8192"
}

