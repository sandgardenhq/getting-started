data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_vpc" "default" {
  default = true
}

# Security group for director
resource "aws_security_group" "sandgarden_director_sg" {
  name        = "${var.namespace}-director-sg"
  description = "Security group for sandgarden director"

  tags = {
    Name = "${var.namespace} Sandgarden Director SG"
  }
}

resource "aws_vpc_security_group_egress_rule" "sandgarden_director_all_outbound" {
  security_group_id = aws_security_group.sandgarden_director_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_ecs_cluster" "sandgarden_director_cluster" {
  name = "sandgarden-director-cluster"
}

resource "aws_ecs_task_definition" "sandgarden_director" {
  family                   = "sandgarden-director-task"
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn 
  task_role_arn     = aws_iam_role.director_role.arn
  network_mode             = "host"
  requires_compatibilities = ["EC2"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  container_definitions = templatefile(
    "./templates/ecs/director.json.tpl",
    {
      "task_cpu"           = var.task_cpu
      "task_memory"        = var.task_memory
      "sand_log_level"        = "DEBUG"
      "sand_api_key_arn"      = aws_secretsmanager_secret.director_api_key.arn
      "sandgarden_ecr_repo_url" = aws_ssm_parameter.ecr_repo_url.value
      "aws_region"            = var.aws_region
      "s3_bucket"             = aws_s3_bucket.director_logs_bucket.bucket
      "sand_cluster"          = var.cluster_name
    }
  )
  depends_on = [aws_cloudwatch_log_group.director]
}

resource "aws_ecs_service" "director-frontend" {
  name            = "sandgarden-director-service"
  cluster         = aws_ecs_cluster.sandgarden_director_cluster.id
  task_definition = aws_ecs_task_definition.sandgarden_director.arn
  desired_count   = 2
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.director_nlb_tg.id
    container_name   = "sandgarden-director-ctr"
    container_port   = 8987
  }
}

resource "aws_cloudwatch_log_group" "director" {
  name              = "/ecs/sandgarden-director"
  retention_in_days = 30

  tags = {
    Name = "${var.namespace}-director-logs"
  }
}

resource "aws_ecs_capacity_provider" "director" {
  name = "${var.namespace}-ecs-ec2"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.director_ecs.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 2
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.sandgarden_director_cluster.name
  capacity_providers = [aws_ecs_capacity_provider.director.name]

  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.director.name
    base              = 1
    weight            = 100
  }
}

resource "aws_appautoscaling_target" "director_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.sandgarden_director_cluster.name}/${aws_ecs_service.director-frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "director_cpu" {
  name               = "${var.namespace}-director-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.director_target.resource_id
  scalable_dimension = aws_appautoscaling_target.director_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.director_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

# HTTPS endpoint for external API access
resource "aws_vpc_endpoint" "https" {
  vpc_id              = data.aws_vpc.default.id
  service_name        = "com.amazonaws.${var.aws_region}.execute-api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = data.aws_subnets.default.ids 
  security_group_ids  = [aws_security_group.sandgarden_director_sg.id]
  private_dns_enabled = false

  tags = {
    Name = "${var.namespace}-https-endpoint"
  }
}