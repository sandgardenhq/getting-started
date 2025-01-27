# Security group for director
resource "aws_security_group" "sandgarden_director_sg" {
  name        = "${var.namespace}-director-sg"
  description = "Security group for sandgarden director"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.namespace} Sandgarden Director SG"
  }
}

# Listen on port 8443
# TODO: make this more appropriate
resource "aws_vpc_security_group_ingress_rule" "director_sg_rule_8443" {
  security_group_id = aws_security_group.sandgarden_director_sg.id
  from_port         = 8443
  to_port           = 8443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "sandgarden_director_all_outbound" {
  security_group_id = aws_security_group.sandgarden_director_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
