#!/usr/bin/env python
import os
import logging
from dotenv import load_dotenv
from cdktf import App, CloudBackend, NamedCloudWorkspace
from stacks.vpn_stack import VpnStack

# Configure logging
logging.getLogger('dotenv').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for CDKTF application"""
    # Load environment variables
    load_dotenv()
    
    # Create CDKTF app
    app = App()
    
    # Get configuration from environment
    region = os.getenv('AWS_REGION', '')
    
    short_region = os.getenv('SHORT_REGION', 'me')
    organization = os.getenv('TERRAFORM_ORGANIZATION', '')
    workspace = os.getenv('TERRAFORM_WORKSPACE', '')
    
    # Validate required environment variables
    required_vars = ['TS_AUTH_KEY', 'TS_AUTH_KEY_2', 'OPENVPN_CONFIG_ENV', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_REGION', 'SHORT_REGION', 'TERRAFORM_ORGANIZATION', 'TERRAFORM_WORKSPACE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create VPN stack
    vpn_stack = VpnStack(
        app, 
        f"aws_instance_{short_region}", 
        region=region, 
        short_region=short_region
    )
    
    # Configure Terraform Cloud backend
    CloudBackend(
        vpn_stack,
        hostname='app.terraform.io',
        organization=organization,
        workspaces=NamedCloudWorkspace(workspace)
    )
    
    # Synthesize the application
    logger.info(f"Deploying VPN stack for region: {region}")
    app.synth()


if __name__ == "__main__":
    main()
