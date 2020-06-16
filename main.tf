# Specify the provider and access details
provider "aws" {
  region = "eu-west-2"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_instance" "ubuntu_instance" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  

  key_name = "BusinessInfra"

  vpc_security_group_ids = [aws_security_group.discord_bot_sg_terraform.id]

  tags = {
    Name = "Movie bot instance"
  }

  user_data = <<EOL
#!/bin/bash
sudo apt update -y
sudo apt-get install python3-venv -y
cd /home/ubuntu
git clone https://github.com/jdockerty/DiscordMovieVoteBot.git
cd DiscordMovieVoteBot
python3 -m venv myenv
source /myenv/bin/activate
pip install -r requirements
EOL
}


resource "aws_security_group" "discord_bot_sg_terraform" {

  name = "discord_bot_sg"
  description = "SG for attaching to Discord bot instance"


  ingress {
    description = "SSH access for debugging"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP access"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

    ingress {
    description = "HTTPS access for OAuth2"
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


  egress {
    description = "Allow all outbound."
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
}
