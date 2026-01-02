# EC2 Instance for Tailscale + OpenVPN Infrastructure

resource "aws_instance" "vpn_gateway" {
  ami           = data.aws_ami.amazon_linux_2023_arm64.id
  instance_type = var.instance_type
  key_name      = var.key_name

  tags = local.final_tags

  user_data_replace_on_change = true

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    tailscale_docker_compose_content = local.tailscale_docker_compose_content
    tailscale_env_content            = local.tailscale_env_content
    openvpn_config                   = local.openvpn_config
    ts_ovpn_docker_compose_content   = local.ts_ovpn_docker_compose_content
    openvpn_ts_env_content           = local.openvpn_ts_env_content
    openvpn_dockerfile_content       = local.openvpn_dockerfile_content
    tailscale_entrypoint_content     = local.tailscale_entrypoint_content
  })
}
