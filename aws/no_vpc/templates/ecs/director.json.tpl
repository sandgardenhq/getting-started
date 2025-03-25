[
  {
    "essential": true,
    "name": "sandgarden-director-ctr",
    "image": "${sandgarden_ecr_repo_url}",
    "privileged": true,
    "cpu": ${task_cpu},
    "memory": ${task_memory},
    "networkMode": "host",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/sandgarden-director",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
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
      },
      {
        "name": "SAND_LOG_DESTINATION",
        "value": "s3://${s3_bucket}"
      }
    ],
    "secrets": [
      {
        "name": "SAND_API_KEY",
        "valueFrom": "${sand_api_key_arn}"
      }
    ],
    "volumesFrom": [],
    "systemControls": [],
    "mountPoints": []
  }
]