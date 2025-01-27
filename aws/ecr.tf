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
