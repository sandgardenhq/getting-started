# Lambda Role ARN
output "lambda_role_arn" {
  value = aws_iam_role.lambda_demo_role.arn
}

# output "nlb_dns" {
#   value = aws_lb.director_nlb.dns_name
# }

output "ecr_registry_url" {
  value = aws_ecr_repository.ecr.repository_url
}
