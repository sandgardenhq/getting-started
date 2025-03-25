output "nlb_dns" {
  value = aws_lb.director_nlb.dns_name
}

output "ecr_registry_url" {
  value = aws_ecr_repository.ecr.repository_url
}
