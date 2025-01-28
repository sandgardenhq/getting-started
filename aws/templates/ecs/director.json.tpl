[
  {
    "essential": true,
    "name": "sandgarden-director-ctr",
    "image": "${sandgarden_ecr_repo_url}",
    "cpu": ${fargate_cpu},
    "memory": ${fargate_memory},
    "networkMode": "awsvpc",
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
        "name": "SAND_HOME",
        "value": "/sandgarden"
      }
    ],
    "secrets": [
      {
        "name": "SAND_API_KEY",
        "valueFrom": "${sand_api_key_arn}"
      }
    ],
    "volumesFrom":[],
    "systemControls":[],
    "mountPoints": [
      {
        "sourceVolume": "config",
        "containerPath": "/sandgarden",
        "readOnly": false
      }
    ],
    "entryPoint": [
      "sh",
      "-c",
      "echo '${staticcfg_content}' > /sandgarden/staticcfg.json && /usr/local/bin/sgdirector serve"
    ]
  }
]