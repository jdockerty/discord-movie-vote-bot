provider "aws" {
  region  = "eu-west-2"
}

resource "aws_security_group" "ecs_bot_default" {
  name        = "ecs-sg"
  description = "SG for outside access"

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

    ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_ecs_cluster" "discord_bot_fargate" {
  name = "discord_movie_bot_fg"
}

resource "aws_ecs_task_definition" "bot_task_def" {
  family                   = "discord_movie_bot_task"
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  cpu                      = 256
  memory                   = 512
  requires_compatibilities = ["FARGATE"]
  container_definitions    = data.template_file.discord_bot_app.rendered

}



resource "aws_ecs_service" "bot_service" {
  name            = "bot_service"
  cluster         = aws_ecs_cluster.discord_bot_fargate.id
  task_definition = aws_ecs_task_definition.bot_task_def.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_bot_default.id]
    subnets          = data.aws_subnet_ids.default.ids
    assign_public_ip = true
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution_role]

}

resource "aws_cloudwatch_log_group" "cw_logs" {
  name = "awslogs-discord-movie-vote-bot"

  tags = {
    Environment = "testing"
    Application = "hive_hr"
  }
}