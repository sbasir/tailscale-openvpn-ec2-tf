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

variable "openvpn_config" {
  description = "OpenVPN configuration"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.nano"
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
