#!/bin/bash
set -e

# Update system and install Docker
dnf update -y
dnf install docker -y
usermod -a -G docker ec2-user
systemctl enable docker.service
systemctl start docker.service

# Enable IP forwarding
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p

# Install Docker Compose
wget https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create configuration files
mkdir -p /home/ec2-user/config

cat > /home/ec2-user/tailscale-docker-compose.yml << 'EOF'
${tailscale_docker_compose_content}
EOF

cat > /home/ec2-user/.tailscale.env << 'EOF'
${tailscale_env_content}
EOF

cat > /home/ec2-user/config.ovpn << 'EOF'
${openvpn_config}
EOF

cat > /home/ec2-user/ts-ovpn-docker-compose.yml << 'EOF'
${ts_ovpn_docker_compose_content}
EOF

cat > /home/ec2-user/.ovpn-ts.env << 'EOF'
${openvpn_ts_env_content}
EOF

cat > /home/ec2-user/openvpn.Dockerfile << 'EOF'
${openvpn_dockerfile_content}
EOF

cat > /home/ec2-user/tailscale-entrypoint.sh << 'EOF'
${tailscale_entrypoint_content}
EOF

chmod +x /home/ec2-user/tailscale-entrypoint.sh

# Start services
cd /home/ec2-user
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts-ovpn -f ts-ovpn-docker-compose.yml up -d
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts -f tailscale-docker-compose.yml up -d
