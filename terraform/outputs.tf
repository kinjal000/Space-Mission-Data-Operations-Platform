output "instance_public_ip" {
  value       = aws_instance.polaris_server.public_ip
  description = "Public IP address of the Polaris EC2 instance"
}

output "vpc_id" {
  value       = aws_vpc.polaris_vpc.id
  description = "Provisioned VPC ID"
}
