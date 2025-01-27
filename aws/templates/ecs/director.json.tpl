[
  {
    "essential": true,
    "name": "sandgarden-director-ctr",
    "image": "${sandgarden_ecr_repo_url}:latest",
    "cpu": ${fargate_cpu},
    "memory": ${fargate_memory},
    "networkMode": "awsvpc",
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/sandgarden/director",
          "awslogs-region": "us-east-2",
          "awslogs-stream-prefix": "sg-director",
          "mode": "non-blocking"
        }
    },
    "portMappings": [
      {
        "protocol": "tcp",
        "containerPort": 8987,
        "hostPort": 8987
      }
    ],
    "environment": [
      {
        "name": "AWS_REGION",
        "value": "${aws_region}"
      },
      {
        "name": "SAND_LOG_LEVEL",
        "value": "${sand_log_level}"
      }
    ],
    "secrets": [
      {
        "name": "SAND_API_KEY",
        "valueFrom": "${sand_api_key_arn}"
      },
    ],
    "volumesFrom":[],
    "systemControls":[],
    "mountPoints":[]
  }
]