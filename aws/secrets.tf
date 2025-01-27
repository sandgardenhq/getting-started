# You must manually input the secrets for the sandgarden director
# into the JSON of this secret
resource "aws_secretsmanager_secret" "director_api_key" {
  name = "${var.namespace}-director-secrets"

  tags = {
    Name = "${var.namespace}-director-secrets"
  }
}

# Add you API key to the secret
resource "aws_secretsmanager_secret_version" "director" {
  secret_id = aws_secretsmanager_secret.director_api_key.id
  secret_string = var.sand_api_key
}

# SSM parameter for director version
resource "aws_ssm_parameter" "director_version" {
  name  = "/${var.namespace}/director/version"
  type  = "String"
  value = "latest"
  lifecycle {
    ignore_changes = [value]
  }

  tags = {
    Name = "${var.namespace}-director-version"
  }
}