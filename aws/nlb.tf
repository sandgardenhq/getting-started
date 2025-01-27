resource "aws_lb" "director_nlb" {
  name               = "${var.namespace}-director-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = var.subnet_ids

  tags = {
    Name = "${var.namespace} Sandgarden Director NLB"
  }
}

resource "aws_lb_target_group" "director_nlb_tg" {
  name        = "${var.namespace}-director-tg"
  port        = 8443
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "ip"

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
