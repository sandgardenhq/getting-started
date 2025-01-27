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

  # load_balancer {
  #   target_group_arn = aws_lb_target_group.director_nlb_tg.id
  #   container_name   = "sandgarden-director-ctr"
  #   container_port   = 8987
  # }
}