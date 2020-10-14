data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = data.aws_vpc.default.id
}

data "template_file" "hive_hr_app" {
  template = file("policies/task-def.json")
  vars = {
    tag      = "latest"
    app_port = 3000
  }
}