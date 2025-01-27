# Secrets ARN
output "director_secret_arn" {
  value = aws_secretsmanager_secret.director_api_key.arn
}

# Lambda Role ARN
output "lambda_role_arn" {
  value = aws_iam_role.lambda_demo_role.arn
}

output "nlb_dns" {
  value = aws_lb.director_nlb.dns_name
}

output "ssm_parameter_name" {
  value = aws_ssm_parameter.director_version.name
}

output "ecr_registry_url" {
  value = aws_ecr_repository.ecr.repository_url
}

output "namespace" {
  value = var.namespace
}
