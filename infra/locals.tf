# Local values and computed configurations

locals {
  # Hostnames for Tailscale services
  ts_hostname_tunnel = "${lower(var.short_region)}-aws-tunnel-ts"
  ts_hostname_ovpn   = "${lower(var.short_region)}-aws-ovpn-${var.openvpn_config_env}"

  # Tags for resources
  default_tags = {
    Name        = "TunnelOpenVPN-${var.short_region}"
    Environment = "production"
    ManagedBy   = "terraform"
  }

  final_tags = merge(local.default_tags, var.tags)

  # Read Docker compose files
  tailscale_docker_compose_content = file("${path.module}/docker/compose/tailscale.docker-compose.yml")
  ts_ovpn_docker_compose_content   = file("${path.module}/docker/compose/ts-ovpn.docker-compose.yml")

  # Read environment templates
  tailscale_env_template_content  = file("${path.module}/config/templates/docker.ts.env.template")
  openvpn_ts_env_template_content = file("${path.module}/config/templates/docker.ts.ovpn.env.template")

  # Read scripts and Dockerfiles
  tailscale_entrypoint_content = file("${path.module}/docker/scripts/tailscale-entrypoint.sh")
  openvpn_dockerfile_content   = file("${path.module}/docker/Dockerfiles/openvpn.Dockerfile")

  # Read OpenVPN configuration
  # Validate that the config file exists before reading
  openvpn_config_path = "${path.module}/config/environments/${var.openvpn_config_env}/config.ovpn"
  openvpn_config      = fileexists(local.openvpn_config_path) ? file(local.openvpn_config_path) : file("ERROR: OpenVPN config file not found at ${local.openvpn_config_path}. Please create the file or check var.openvpn_config_env value.")

  # Substitute variables in environment templates
  tailscale_env_content = replace(
    replace(
      local.tailscale_env_template_content,
      "$${TS_AUTH_KEY}", var.ts_auth_key
    ),
    "$${TS_HOSTNAME}", local.ts_hostname_tunnel
  )

  openvpn_ts_env_content = replace(
    replace(
      local.openvpn_ts_env_template_content,
      "$${TS_AUTH_KEY}", var.ts_auth_key
    ),
    "$${TS_HOSTNAME}", local.ts_hostname_ovpn
  )
}
