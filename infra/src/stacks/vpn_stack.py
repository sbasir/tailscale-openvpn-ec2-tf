#!/usr/bin/env python
import os
from constructs import Construct
from cdktf import TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.data_aws_ami import DataAwsAmi, DataAwsAmiFilter
from cdktf_cdktf_provider_aws.instance import Instance


class VpnStack(TerraformStack):
    """CDKTF Stack for Tailscale + OpenVPN infrastructure"""
    
    def __init__(self, scope: Construct, id: str, region: str, short_region: str):
        super().__init__(scope, id)
        
        self.region = region
        self.short_region = short_region
        
        # Initialize AWS provider
        self._setup_aws_provider()
        
        # Load configuration files
        self._load_config_files()
        
        # Load environment variables
        self._load_environment_variables()
        
        # Create infrastructure
        self._create_infrastructure()
    
    def _setup_aws_provider(self):
        """Setup AWS provider with credentials"""
        AwsProvider(
            self, 'aws',
            region=self.region,
            access_key=os.getenv('AWS_ACCESS_KEY_ID', ''),
            secret_key=os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            token=os.getenv('AWS_SESSION_TOKEN', '')
        )
    
    def _load_config_files(self):
        """Load all configuration files"""
        config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
        docker_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docker')
        
        # Load Docker compose files
        with open(os.path.join(docker_dir, 'compose', 'tailscale.docker-compose.yml'), 'r') as f:
            self.tailscale_docker_compose_content = f.read()
        
        with open(os.path.join(docker_dir, 'compose', 'ts-ovpn.docker-compose.yml'), 'r') as f:
            self.ts_ovpn_docker_compose_content = f.read()
        
        # Load environment templates
        with open(os.path.join(config_dir, 'templates', 'docker.ts.env.template'), 'r') as f:
            self.tailscale_env_content = f.read()
        
        with open(os.path.join(config_dir, 'templates', 'docker.ts.ovpn.env.template'), 'r') as f:
            self.openvpn_ts_env_content = f.read()
        
        # Load scripts and Dockerfiles
        with open(os.path.join(docker_dir, 'scripts', 'tailscale-entrypoint.sh'), 'r') as f:
            self.tailscale_entrypoint_content = f.read()
        
        with open(os.path.join(docker_dir, 'Dockerfiles', 'openvpn.Dockerfile'), 'r') as f:
            self.openvpn_dockerfile_content = f.read()
    
    def _load_environment_variables(self):
        """Load and validate environment variables"""
        self.ts_auth_key = os.getenv('TS_AUTH_KEY', '')
        self.openVpnConfigEnv = os.getenv('OPENVPN_CONFIG_ENV', '')
        
        if not self.ts_auth_key:
            raise ValueError("TS_AUTH_KEY environment variables are required")
        
        # Load OpenVPN config
        config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'environments', self.openVpnConfigEnv)
        openvpn_config_path = os.path.join(config_dir, 'config.ovpn')
        
        if not os.path.exists(openvpn_config_path):
            raise FileNotFoundError(f"OpenVPN config file not found: {openvpn_config_path}")
        
        with open(openvpn_config_path, 'r') as f:
            self.openvpn_config = f.read()
    
    def _substitute_variables(self):
        """Substitute variables in configuration templates"""
        # Substitute in Tailscale environment content
        self.tailscale_env_content = self.tailscale_env_content.replace('${TS_AUTH_KEY}', self.ts_auth_key)
        self.tailscale_env_content = self.tailscale_env_content.replace('${TS_HOSTNAME}', f'{self.short_region.lower()}-aws-tunnel-ts')
        self.tailscale_env_content = self.tailscale_env_content.replace('${TS_SOCKET}', '/var/run/tailscale/tailscaled.sock')
        
        # Substitute in OpenVPN Tailscale environment content
        self.openvpn_ts_env_content = self.openvpn_ts_env_content.replace('${TS_AUTH_KEY}', self.ts_auth_key)
        self.openvpn_ts_env_content = self.openvpn_ts_env_content.replace('${TS_HOSTNAME}', f'{self.short_region.lower()}-aws-ovpn-platform-internal')
        self.openvpn_ts_env_content = self.openvpn_ts_env_content.replace('${TS_SOCKET}', '/var/run/tailscale/ovpn-tailscaled.sock')
        
        # Substitute in entrypoint script
        self.tailscale_entrypoint_content = self.tailscale_entrypoint_content.replace('$$TS_AUTH_KEY', self.ts_auth_key)
        self.tailscale_entrypoint_content = self.tailscale_entrypoint_content.replace('$$TS_HOSTNAME', f'{self.short_region.lower()}-aws-ovpn-platform-internal')
        self.tailscale_entrypoint_content = self.tailscale_entrypoint_content.replace('$$TS_EXTRA_ARGS', '--advertise-exit-node --accept-routes')
    
    def _create_infrastructure(self):
        """Create the main infrastructure"""
        # Substitute variables
        self._substitute_variables()
        
        # Get latest Amazon Linux 2023 AMI
        ami = DataAwsAmi(
            self, 'ami',
            most_recent=True,
            owners=['amazon'],
            filter=[DataAwsAmiFilter(
                name='name',
                values=['al2023-ami-2023.*-arm64']
            )]
        )
        
        # Create EC2 instance
        self.instance = Instance(
            self, 'instance',
            ami=ami.image_id,
            instance_type='t4g.nano',
            key_name='tailscale-nord-me',
            tags={
                'Name': f'TunnelOpenVPN-{self.short_region}',
                'Environment': 'production',
                'ManagedBy': 'cdktf'
            },
            user_data_replace_on_change=True,
            user_data=self._generate_user_data()
        )
        
        # Create outputs
        TerraformOutput(self, 'instance_public_ip', value=self.instance.public_ip)
        TerraformOutput(self, 'instance_id', value=self.instance.id)
    
    def _generate_user_data(self):
        """Generate user data script for EC2 instance"""
        return f"""#!/bin/bash
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
{self.tailscale_docker_compose_content}
EOF

cat > /home/ec2-user/.tailscale.env << 'EOF'
{self.tailscale_env_content}
EOF

cat > /home/ec2-user/config.ovpn << 'EOF'
{self.openvpn_config}
EOF

cat > /home/ec2-user/ts-ovpn-docker-compose.yml << 'EOF'
{self.ts_ovpn_docker_compose_content}
EOF

cat > /home/ec2-user/.ovpn-ts.env << 'EOF'
{self.openvpn_ts_env_content}
EOF

cat > /home/ec2-user/openvpn.Dockerfile << 'EOF'
{self.openvpn_dockerfile_content}
EOF

cat > /home/ec2-user/tailscale-entrypoint.sh << 'EOF'
{self.tailscale_entrypoint_content}
EOF

chmod +x /home/ec2-user/tailscale-entrypoint.sh

# Start services
cd /home/ec2-user
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts-ovpn -f ts-ovpn-docker-compose.yml up -d
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts -f tailscale-docker-compose.yml up -d
""" 