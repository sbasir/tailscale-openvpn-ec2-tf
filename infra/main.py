#!/usr/bin/env python
import os
from dotenv import load_dotenv
from constructs import Construct
from cdktf import App, TerraformStack, CloudBackend, NamedCloudWorkspace, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.data_aws_ami import DataAwsAmi, DataAwsAmiFilter
from cdktf_cdktf_provider_aws.instance import Instance

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, region: str, shortRegion: str):
        super().__init__(scope, id)

        AwsProvider(self, 'aws', 
            region=region,
            access_key=os.getenv('AWS_ACCESS_KEY_ID', ''),
            secret_key=os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            token=os.getenv('AWS_SESSION_TOKEN', '')
        )

        ami = DataAwsAmi(self, 'ami',
            most_recent=True,
            owners=['amazon'],
            filter=[DataAwsAmiFilter(name='name', values=['al2023-ami-2023.*-arm64'])])

        with open('tailscale.docker-compose.yml', 'r') as f:
            tailscaleDockerComposeContent = f.read()
        
        with open('docker.ts.env.template', 'r') as f:
            tailscaleEnvContent = f.read()

        with open('docker.ts.ovpn.env.template', 'r') as f:
            openVpnTsEnvContent = f.read()

        with open('ts-ovpn.docker-compose.yml', 'r') as f:
            tsOvpnDockerComposeContent = f.read()

        with open('tailscale-entrypoint.sh', 'r') as f:
            tailscaleEntrypointContent = f.read()

        load_dotenv()
        ts_auth_key = os.getenv('TS_AUTH_KEY', '')
        ts_auth_key_2 = os.getenv('TS_AUTH_KEY_2', '')
        openVpnConfigFile = os.getenv('OPENVPN_CONFIG_FILE', 'config.ovpn')
        
        with open(openVpnConfigFile, 'r') as f:
            openVpnConfig = f.read()
        
        tailscaleEnvContent = tailscaleEnvContent.replace('${TS_AUTH_KEY}', ts_auth_key)
        tailscaleEnvContent = tailscaleEnvContent.replace('${TS_HOSTNAME}', f'{shortRegion.lower()}-aws-tunnel-ts')
        tailscaleEnvContent = tailscaleEnvContent.replace('${TS_SOCKET}', '/var/run/tailscale/tailscaled.sock')

        openVpnTsEnvContent = openVpnTsEnvContent.replace('${TS_AUTH_KEY}', ts_auth_key_2)
        openVpnTsEnvContent = openVpnTsEnvContent.replace('${TS_HOSTNAME}', f'{shortRegion.lower()}-aws-ovpn-platform-internal')
        openVpnTsEnvContent = openVpnTsEnvContent.replace('${TS_SOCKET}', '/var/run/tailscale/ovpn-tailscaled.sock')

        with open('openvpn.Dockerfile', 'r') as f:
            openVpnDockerfileContent = f.read()

        instance = Instance(self, 'instance',
            ami=ami.image_id,
            instance_type='t4g.nano',
            key_name='tailscale-nord-me',
            tags={
                'Name': f'TunnelOpenVPN-{shortRegion}'
            },
            user_data_replace_on_change=True,
            user_data=f"""#!/bin/bash
dnf update
dnf install docker -y
usermod -a -G docker ec2-user
id ec2-user
newgrp docker

echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p

wget https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) 
mv docker-compose-$(uname -s)-$(uname -m) /usr/local/bin/docker-compose
chmod -v +x /usr/local/bin/docker-compose
systemctl enable docker.service
systemctl start docker.service

cat > /home/ec2-user/tailscale-docker-compose.yml << EOF
{tailscaleDockerComposeContent}
EOF

cat > /home/ec2-user/.tailscale.env << EOF
{tailscaleEnvContent}
EOF

cat > /home/ec2-user/config.ovpn << EOF
{openVpnConfig}
EOF

cat > /home/ec2-user/ts-ovpn-docker-compose.yml << EOF
{tsOvpnDockerComposeContent}
EOF

cat > /home/ec2-user/.ovpn-ts.env << EOF
{openVpnTsEnvContent}
EOF

cat > /home/ec2-user/openvpn.Dockerfile << EOF
{openVpnDockerfileContent}
EOF

cat > /home/ec2-user/tailscale-entrypoint.sh << EOF
{tailscaleEntrypointContent}
EOF

chmod +x /home/ec2-user/tailscale-entrypoint.sh

cd /home/ec2-user
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts -f tailscale-docker-compose.yml up -d
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts-ovpn -f ts-ovpn-docker-compose.yml up -d
"""
        )

        TerraformOutput(self, 'instance_public_ip', value=instance.public_ip)


app = App()
meStack = MyStack(app, "aws_instance_me", 'me-central-1', 'me')
CloudBackend(meStack,
  hostname='app.terraform.io',
  organization='SB_dev',
  workspaces=NamedCloudWorkspace('tailscale-openvpn-me')
)

app.synth()
