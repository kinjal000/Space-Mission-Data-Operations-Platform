provider "aws" {
  region = var.aws_region
}

# 1. Create VPC
resource "aws_vpc" "polaris_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "polaris-vpc"
  }
}

# 2. Create Internet Gateway
resource "aws_internet_gateway" "polaris_igw" {
  vpc_id = aws_vpc.polaris_vpc.id

  tags = {
    Name = "polaris-igw"
  }
}

# 3. Create Public Subnet
resource "aws_subnet" "polaris_subnet" {
  vpc_id                  = aws_vpc.polaris_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "polaris-subnet"
  }
}

# 4. Create Route Table
resource "aws_route_table" "polaris_rt" {
  vpc_id = aws_vpc.polaris_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.polaris_igw.id
  }

  tags = {
    Name = "polaris-route-table"
  }
}

# 5. Associate Route Table with Subnet
resource "aws_route_table_association" "polaris_rta" {
  subnet_id      = aws_subnet.polaris_subnet.id
  route_table_id = aws_route_table.polaris_rt.id
}

# 6. Create Security Group
resource "aws_security_group" "polaris_sg" {
  name        = "polaris-sg"
  description = "Allow inbound HTTP and SSH traffic"
  vpc_id      = aws_vpc.polaris_vpc.id

  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Flask Custom Port"
    from_port   = 5006
    to_port     = 5006
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "polaris-security-group"
  }
}

# 7. Fetch latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 8. Create EC2 Instance
resource "aws_instance" "polaris_server" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.polaris_subnet.id
  vpc_security_group_ids = [aws_security_group.polaris_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo amazon-linux-extras install docker -y
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              EOF

  tags = {
    Name = "polaris-operations-server"
  }
}
