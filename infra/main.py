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
        
        with open('docker.env.template', 'r') as f:
            tailscaleEnvContent = f.read()
        
        tailscaleEnvContent = tailscaleEnvContent.replace('${TS_HOSTNAME}', f'{shortRegion.lower()}-aws-tunnel-ts')
        # Load .env file and get TS_TOKEN
        load_dotenv()
        ts_auth_key = os.getenv('TS_AUTH_KEY', '')
        
        tailscaleEnvContent = tailscaleEnvContent.replace('${TS_AUTH_KEY}', ts_auth_key)

        instance = Instance(self, 'instance',
            ami=ami.image_id,
            instance_type='t4g.nano',
            key_name='tailscale-nord-me',
            tags={
                'Name': f'TunnelOpenVPN-{shortRegion}'
            },
            user_data_replace_on_change=True,
            user_data=f"""
#!/bin/bash
dnf update
dnf install docker -y
usermod -a -G docker ec2-user
id ec2-user
newgrp docker

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
TS_SOCKET=/var/run/tailscale/tailscaled.sock
EOF

cd /home/ec2-user
COMPOSE_BAKE=true /usr/local/bin/docker-compose -p ts -f tailscale-docker-compose.yml up -d
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
