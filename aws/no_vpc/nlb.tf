resource "aws_lb" "director_nlb" {
  name               = "${var.namespace}-director-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = data.aws_subnets.default.ids
  security_groups    = [aws_security_group.nlb_sg.id]

  tags = {
    Name = "${var.namespace} Director NLB"
  }
}

resource "aws_lb_target_group" "director_nlb_tg" {
  name        = "${var.namespace}-director-tg"
  port        = 8987
  protocol    = "TCP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id

  health_check {
    protocol            = "TCP"
    port                = 8987
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval           = 30
  }
}

resource "aws_lb_listener" "director_nlb" {
  load_balancer_arn = aws_lb.director_nlb.arn
  port              = 443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.director_nlb_tg.arn
  }
}

# Security group for NLB
resource "aws_security_group" "nlb_sg" {
  name        = "${var.namespace}-nlb-sg-2"
  description = "Security group for Network Load Balancer"

  tags = {
    Name = "${var.namespace}-nlb-sg"
  }
}

# Allow inbound HTTPS to NLB
resource "aws_vpc_security_group_ingress_rule" "nlb_https" {
  security_group_id = aws_security_group.nlb_sg.id
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow HTTPS inbound"
}

# Allow NLB to ECS traffic
resource "aws_vpc_security_group_ingress_rule" "ecs_from_nlb" {
  security_group_id = aws_security_group.sandgarden_director_sg.id
  from_port         = 8987
  to_port           = 8987
  ip_protocol       = "tcp"
  description       = "Allow traffic from NLB"
  referenced_security_group_id = aws_security_group.nlb_sg.id
}
