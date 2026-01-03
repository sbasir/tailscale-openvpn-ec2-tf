# EC2 Instance for Tailscale + OpenVPN Infrastructure

# IAM Role for EC2 instance to use SSM
resource "aws_iam_role" "ec2_ssm_role" {
  name = "ec2-ssm-role-${var.short_region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "EC2-SSM-Role"
  }
}

# Attach the AWS managed policy for SSM
resource "aws_iam_role_policy_attachment" "ec2_ssm_policy" {
  role       = aws_iam_role.ec2_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Create instance profile
resource "aws_iam_instance_profile" "ec2_ssm_profile" {
  name = "ec2-ssm-profile-${var.short_region}"
  role = aws_iam_role.ec2_ssm_role.name

  tags = {
    Name = "EC2-SSM-Profile"
  }
}

resource "aws_instance" "vpn_gateway" {
  ami           = data.aws_ami.amazon_linux_2023_arm64.id
  instance_type = var.instance_type

  tags = local.final_tags

  user_data_replace_on_change = true

  iam_instance_profile = aws_iam_instance_profile.ec2_ssm_profile.name

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    tailscale_docker_compose_content = local.tailscale_docker_compose_content
    tailscale_env_content            = local.tailscale_env_content
    openvpn_config                   = var.openvpn_config
    ts_ovpn_docker_compose_content   = local.ts_ovpn_docker_compose_content
    openvpn_ts_env_content           = local.openvpn_ts_env_content
    openvpn_dockerfile_content       = local.openvpn_dockerfile_content
    tailscale_entrypoint_content     = local.tailscale_entrypoint_content
  })
}
