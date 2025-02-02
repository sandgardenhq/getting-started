resource "aws_iam_role" "director_role" {
  name = "${var.namespace}-director-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ecs-tasks.amazonaws.com",
            "ec2.amazonaws.com"
          ]
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
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecrets"
    ]
    resources = [
      aws_secretsmanager_secret.director_api_key.arn,
      "${aws_secretsmanager_secret.director_api_key.arn}-??????"  # For secret versions
    ]
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

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
      "logs:GetLogEvents",
      "logs:DescribeLogGroups"
    ]
    resources = [
      "${aws_cloudwatch_log_group.director.arn}:*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:GetRepositoryPolicy",
      "ecr:SetRepositoryPolicy"
    ]
    resources = [
      aws_ecr_repository.ecr.arn,
      "${aws_ecr_repository.ecr.arn}/*",
      "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.account_id}:repository/sgdirector-cache/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "sts:GetServiceBearerToken"
    ]
    resources = ["*"]
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

resource "aws_iam_role_policy_attachment" "ecs_node_role_policy" {
  role       = aws_iam_role.director_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "director_policy_attachment" {
  role       = aws_iam_role.director_role.name
  policy_arn = aws_iam_policy.director_policy.arn
}

resource "aws_iam_role_policy_attachment" "execution_role_attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.director_policy.arn
}

resource "aws_iam_role_policy_attachment" "director_managed_core" {
  role       = aws_iam_role.director_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Create separate execution role for ECS tasks
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.namespace}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Add a specific policy for secrets access to the execution role
resource "aws_iam_role_policy" "execution_secrets_policy" {
  name = "${var.namespace}-execution-secrets-policy"
  role = aws_iam_role.ecs_task_execution_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.director_api_key.arn,
          "${aws_secretsmanager_secret.director_api_key.arn}-??????"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "execution_logs_policy" {
  name = "${var.namespace}-execution-logs-policy"
  role = aws_iam_role.ecs_task_execution_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.director.arn}:*"
        ]
      }
    ]
  })
}