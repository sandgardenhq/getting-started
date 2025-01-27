# Example Lambda Demo policy
resource "aws_iam_policy" "lambda_demo" {
  name = "${var.namespace}-lambda-demo"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })

  tags = {
    Name = "${var.namespace}-lambda-demo"
  }
}

resource "aws_iam_role" "lambda_demo_role" {
  name = "${var.namespace}-lambda-demo-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.namespace}-lambda-role"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_demo_policy_attachment" {
  role       = aws_iam_role.lambda_demo_role.name
  policy_arn = aws_iam_policy.lambda_demo.arn
}

resource "aws_iam_role_policy_attachment" "lambda_demo_policy_basic" {
  role       = aws_iam_role.lambda_demo_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_demo_policy_vpc_access" {
  role       = aws_iam_role.lambda_demo_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}
