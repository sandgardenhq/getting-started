resource "aws_iam_role" "director_role" {
  name = "${var.namespace}-director-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.namespace}-director-role"
  }
}

data "aws_iam_policy_document" "director_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
    ]
    resources = [aws_ssm_parameter.director_version.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.director_binaries.arn,
      "${aws_s3_bucket.director_binaries.arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
    ]
    resources = [aws_ssm_parameter.director_version.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
    ]
    resources = [aws_secretsmanager_secret.director_api_key.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:*",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeVpcs",
      "ec2:DescribeSecurityGroups",
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSubnets",
      "ec2:DeleteNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses"
    ]
    resources = ["*"]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
      "lambda:InvokeFunction",
      "lambda:DeleteFunction",
      "lambda:GetFunction",
      "lambda:ListFunctions"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "director_policy" {
  name   = "${var.namespace}-director-policy"
  policy = data.aws_iam_policy_document.director_policy.json
}

resource "aws_iam_instance_profile" "director_profile" {
  name = "${var.namespace}-director-profile"
  role = aws_iam_role.director_role.name

  tags = {
    Name = "${var.namespace}-director-profile"
  }
}

resource "aws_iam_role_policy_attachment" "director_policy_attachment" {
  role       = aws_iam_role.director_role.name
  policy_arn = aws_iam_policy.director_policy.arn
}

resource "aws_iam_role_policy_attachment" "director_managed_core" {
  role       = aws_iam_role.director_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
