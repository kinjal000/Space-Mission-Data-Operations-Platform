variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS Region to provision resources in"
}

variable "instance_type" {
  type        = string
  default     = "t2.micro"
  description = "EC2 instance size for Flask server deployment"
}
