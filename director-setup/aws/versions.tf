data "external" "latest_director_version" {
  program = ["bash", "-c", <<-EOT
    VERSION=$(aws ecr-public describe-image-tags \
      --repository-name sandgarden/sgdirector \
      --region us-east-1 \
      --query 'imageTagDetails[?imageTag!=`latest`]|[0].imageTag' \
      --output text)
    echo "{\"version\": \"$VERSION\"}"
  EOT
  ]
}

locals {
  director_version = coalesce(var.director_version, data.external.latest_director_version.result.version)
} 