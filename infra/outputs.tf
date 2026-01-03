# Outputs for the infrastructure

output "instance_public_ip" {
  description = "Public IP address of the VPN gateway EC2 instance"
  value       = aws_instance.vpn_gateway.public_ip
}

output "instance_id" {
  description = "ID of the VPN gateway EC2 instance"
  value       = aws_instance.vpn_gateway.id
}

output "instance_arn" {
  description = "ARN of the VPN gateway EC2 instance"
  value       = aws_instance.vpn_gateway.arn
}

output "tailscale_hostname" {
  description = "Hostname of the Tailscale OpenVPN gateway"
  value       = local.ts_hostname_ovpn
}
