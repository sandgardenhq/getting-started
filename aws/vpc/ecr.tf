resource "aws_ecr_repository" "ecr" {
  name                 = "${var.namespace}-director-ecr"
  image_tag_mutability = "MUTABLE"

  tags = {
    Name = "${var.namespace}-director-ecr"
  }
}

locals {
  ecr_repo_name    = split("/", aws_ecr_repository.ecr.repository_url)[1]
  ecr_registry_url = split("/", aws_ecr_repository.ecr.repository_url)[0]
}

resource "aws_ecr_pull_through_cache_rule" "public" {
  ecr_repository_prefix = "sgdirector-cache"
  upstream_registry_url = var.sandgarden_ecr_repo_url
}

# Update the repository URL in variables
resource "aws_ssm_parameter" "ecr_repo_url" {
  name  = "/${var.namespace}/ecr/repo_url"
  type  = "String"
  value = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/sgdirector-cache/h7j2x0j6/sgdirector:${local.director_version}"
}

data "aws_caller_identity" "current" {}
