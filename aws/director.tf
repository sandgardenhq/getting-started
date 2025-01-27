# Security group for director
resource "aws_security_group" "sandgarden_director_sg" {
  name        = "${var.namespace}-director-sg"
  description = "Security group for sandgarden director"
  vpc_id      = var.vpc_id

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
  execution_role_arn       = aws_iam_role.director_role.arn
  task_role_arn            = aws_iam_role.director_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions = templatefile(
    "./templates/ecs/director.json.tpl",
    {
      "fargate_cpu"           = var.fargate_cpu
      "fargate_memory"        = var.fargate_memory
      "sand_log_level"        = "DEBUG"
      "sand_api_key_arn"      = aws_secretsmanager_secret.director_api_key.arn
      "sandgarden_ecr_repo_url" = var.sandgarden_ecr_repo_url
      "aws_region"            = var.aws_region
    }
  )
}

resource "aws_ecs_service" "director-frontend" {
  name            = "sandgarden-director-service"
  cluster         = aws_ecs_cluster.sandgarden_director_cluster.id
  task_definition = aws_ecs_task_definition.sandgarden_director.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.sandgarden_director_sg.id]
    subnets          = var.subnet_ids
    assign_public_ip = false
  }

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

resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [aws_security_group.sandgarden_director_sg.id]
  private_dns_enabled = true

  tags = {
    Name = "${var.namespace}-secretsmanager-endpoint"
  }
}

resource "aws_vpc_security_group_ingress_rule" "director_secretsmanager" {
  security_group_id = aws_security_group.sandgarden_director_sg.id
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  description       = "Allow HTTPS access to Secrets Manager VPC Endpoint"
  referenced_security_group_id = aws_security_group.sandgarden_director_sg.id
}