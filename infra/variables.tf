# Variables for Tailscale OpenVPN EC2 Infrastructure

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "short_region" {
  description = "Short identifier for the region (e.g., 'me' for Middle East)"
  type        = string
}

variable "ts_auth_key" {
  description = "Tailscale authentication key"
  type        = string
  sensitive   = true
}

variable "openvpn_config_env" {
  description = "OpenVPN configuration environment (e.g., 'prod', 'non-prod')"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.nano"
}

variable "key_name" {
  description = "AWS EC2 key pair name for SSH access"
  type        = string
  default     = "tailscale-nord-me"
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
