# Tailscale OpenVPN EC2 Bridge

A Terraform project that deploys a VPN bridge infrastructure on AWS EC2, allowing Tailscale clients to seamlessly access corporate resources through OpenVPN tunnels.

> **📢 Migration Notice**: This project has been migrated from CDKTF to vanilla Terraform. See [MIGRATION.md](MIGRATION.md) for details.

## What It Is

This project creates a **VPN gateway** that bridges Tailscale's mesh networking with traditional OpenVPN connections. It deploys a containerized solution on AWS EC2 that acts as a gateway, enabling your Tailscale-connected devices to access corporate networks through OpenVPN without managing multiple VPN clients.

## What It Does

The infrastructure creates a **VPN bridge** that:

- **Connects Tailscale mesh network** to corporate OpenVPN networks
- **Routes traffic** between Tailscale clients and corporate resources
- **Provides centralized gateway** for corporate network access
- **Manages IP forwarding and NAT** using iptables rules
- **Runs containerized services** for Tailscale and OpenVPN on EC2

## Why Use This Solution

### For Remote Workers
- **Single VPN client**: Use only Tailscale on your devices while accessing corporate networks
- **Simplified management**: No need to manage multiple VPN clients or configurations
- **Seamless access**: Corporate resources appear as directly accessible through Tailscale

### For Organizations
- **Centralized control**: All corporate access flows through a monitored gateway
- **Multi-network support**: Access multiple corporate networks through different OpenVPN configs
- **Security**: Traffic is controlled, monitored, and logged through a single gateway
- **Scalability**: Easy to deploy multiple gateways for different regions or networks

### Technical Benefits
- **Device management**: Leverage Tailscale's superior device management and authentication
- **Network isolation**: Corporate networks remain isolated while providing controlled access
- **Monitoring**: All traffic can be monitored and logged for security compliance

## Architecture

The solution creates a VPN chain where Tailscale provides mesh networking and OpenVPN provides corporate access:

```mermaid
graph TB
    subgraph "AWS EC2 Instance"
        subgraph "Docker Container"
            TS[Tailscale Daemon<br/>tailscale0 interface]
            OVPN[OpenVPN Client<br/>tun0 interface]
            
            TS -.->|"Rule 1: FORWARD<br/>tailscale0 → tun0"| OVPN
            OVPN -.->|"Rule 2: FORWARD<br/>tun0 → tailscale0"| TS
        end
        
        subgraph "iptables NAT"
            NAT[MASQUERADE<br/>100.64.0.0/10 → tun0]
        end
    end
    
    subgraph "External Networks"
        TSNet[Tailscale Network<br/>100.64.0.0/10]
        VPNNet[OpenVPN Network<br/>Corporate VPN]
    end
    
    TSNet <--> TS
    OVPN <--> VPNNet
    TS --> NAT
    NAT --> OVPN
    
    style TS fill:#e1f5fe
    style OVPN fill:#f3e5f5
    style NAT fill:#fff3e0
    style TSNet fill:#e8f5e8
    style VPNNet fill:#fce4ec
```

### How It Works

1. **Tailscale clients** send traffic to corporate resources (e.g., 10.1.1.100)
2. **Gateway receives** traffic via Tailscale interface (`tailscale0`)
3. **iptables rules** forward traffic from `tailscale0` to OpenVPN tunnel (`tun0`)
4. **NAT/MASQUERADE** changes source IP from Tailscale range to tunnel IP
5. **OpenVPN tunnel** sends traffic to corporate network
6. **Return traffic** follows the reverse path back to Tailscale clients

## Tech Stack

- **Infrastructure**: AWS EC2 (Amazon Linux 2023 ARM64)
- **Infrastructure as Code**: Terraform (HashiCorp Configuration Language)
- **Containerization**: Docker & Docker Compose
- **VPN Technologies**: 
  - Tailscale (mesh networking)
  - OpenVPN (corporate access)
- **Networking**: iptables, IP forwarding, NAT
- **Cloud Provider**: AWS
- **Backend**: Terraform Cloud

## Prerequisites

### Required

- **Terraform CLI** (version 1.0 or later) - [install guide](https://www.terraform.io/downloads)
- **AWS Account** with appropriate permissions
- **AWS CLI** configured with credentials
- **Tailscale Account** with auth keys
- **OpenVPN Configuration** files for corporate networks
- **Terraform Cloud** account for state management

## Quick Start

### 1. Clone and Install Terraform

```bash
git clone https://github.com/sbasir/tailscale-openvpn-ec2-cdktf
cd tailscale-openvpn-ec2-cdktf
```

**Install Terraform** if not already installed:

```bash
# macOS
brew install terraform

# Linux - see https://www.terraform.io/downloads
# Or use your package manager
```

### 2. Configure Variables

Create a variables file:

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
aws_region         = "me-central-1"
short_region       = "me"
ts_auth_key        = "tskey-auth-xxxxxxxxxxxxx"
openvpn_config_env = "prod"
```

Alternatively, set environment variables:

```bash
export TF_VAR_aws_region="me-central-1"
export TF_VAR_short_region="me"
export TF_VAR_ts_auth_key="your_tailscale_auth_key"
export TF_VAR_openvpn_config_env="prod"
```

### 3. Configure Terraform Cloud Backend

Authenticate with Terraform Cloud:

```bash
terraform login
```

Or set the token as an environment variable:

```bash
export TF_TOKEN_app_terraform_io="your-terraform-cloud-token"
```

### 4. Add OpenVPN Configuration

Place your OpenVPN configuration file (e.g., for `prod`):

```bash
mkdir -p infra/config/environments/prod
# Copy your config.ovpn file to infra/config/environments/prod/config.ovpn
```

### 5. Initialize and Deploy Infrastructure

```bash
cd infra

# Set Terraform Cloud configuration
export TF_CLOUD_ORGANIZATION="your_terraform_organization"
export TF_WORKSPACE="your_workspace"

# Initialize Terraform (first time only)
terraform init

# Review the plan
terraform plan

# Deploy
terraform apply
```

Or use the Makefile:

```bash
make init
make plan
make apply
```

### 5. Configure Tailscale (Post-Deployment)

After deployment, you need to configure Tailscale to use the gateway:

#### Approve Routes and Exit Node

1. **Access Tailscale Admin**: Go to [https://login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)

2. **Find Your Gateway**: Look for the machine with hostname pattern `{region}-aws-ovpn-{env}`

3. **Approve Subnet Routes**: 
   - Click on the gateway machine
   - Go to "Route settings" 
   - Approve the routes that the gateway is advertising (typically corporate network subnets)
   - See [Tailscale Subnet Routing Documentation](https://tailscale.com/kb/1019/subnets)

4. **Enable Exit Node** (if configured):
   - In the same machine settings, enable "Exit node" if you want to route all traffic through the gateway
   - See [Tailscale Exit Node Documentation](https://tailscale.com/kb/1103/exit-nodes)

5. **Wait for Registration**: Give the machines 2-5 minutes to register and sync settings

#### Using the Gateway

On your Tailscale clients:

```bash
# Use specific routes (recommended)
tailscale up --accept-routes

# Or use as exit node (routes all traffic)
tailscale up --exit-node={gateway-ip}
```

## Configuration

### Directory Structure

```
infra/
├── config/
│   ├── environments/         # Environment-specific OpenVPN configs
│   │   ├── prod/
│   │   │   └── config.ovpn   # Production OpenVPN config
│   │   └── non-prod/
│   │       └── config.ovpn   # Non Production OpenVPN config
│   └── templates/            # Configuration templates
├── docker/                   # Docker configurations
│   ├── compose/              # Docker Compose files
│   ├── Dockerfiles/          # Custom Dockerfiles
│   └── scripts/              # Entrypoint scripts
├── *.tf                      # Terraform configuration files
├── terraform.tfvars.example  # Example variables file
├── user_data.sh.tpl          # EC2 user data template
└── Makefile                  # Helper commands
```

### Terraform Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `aws_region` | AWS region to deploy to | ✓ | - |
| `short_region` | Short region identifier | ✓ | - |
| `ts_auth_key` | Tailscale auth key | ✓ | - |
| `openvpn_config_env` | OpenVPN config environment | ✓ | - |
| `instance_type` | EC2 instance type | ✗ | `t4g.nano` |
| `key_name` | AWS EC2 key pair name | ✗ | `tailscale-nord-me` |
| `tags` | Additional resource tags | ✗ | `{}` |

### AWS Credentials

AWS credentials can be provided via:
- AWS CLI configuration (`~/.aws/credentials`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
- IAM role (when running on EC2 or in CI/CD)

## Management Commands

All commands should be run from the `infra/` directory:

```bash
# Using Terraform directly
terraform init    # Initialize (first time only)
terraform plan    # View deployment plan
terraform apply   # Deploy infrastructure
terraform destroy # Destroy infrastructure
terraform fmt     # Format Terraform files
terraform validate # Validate configuration

# Using Makefile (recommended)
make help     # Show available commands
make init     # Initialize Terraform
make plan     # View deployment plan
make apply    # Deploy infrastructure
make destroy  # Destroy infrastructure
make validate # Validate and check formatting
make fmt      # Format Terraform files
make clean    # Clean up Terraform files
```

## Networking Details

For detailed information about the network architecture, iptables rules, and packet flow, see the [Network Documentation](infra/docs/NETWORK.md).

## Security Considerations

- **Firewall Rules**: Only necessary ports are opened
- **NAT**: Tailscale IPs are hidden from corporate network
- **Container Isolation**: Services run in separate containers
- **Traffic Monitoring**: All traffic can be monitored and logged
- **Access Control**: Tailscale provides device authentication and authorization

## Troubleshooting

### Common Issues

1. **Terraform Init Fails**: 
   - Ensure you've authenticated with Terraform Cloud (`terraform login`)
   - Check organization and workspace names are correct
   - Verify `TF_API_TOKEN` environment variable if using CI/CD

2. **Variable Errors**: 
   - Create `terraform.tfvars` from the example file
   - Or set environment variables with `TF_VAR_` prefix
   - Ensure all required variables are provided

3. **Deployment Fails**: 
   - Check AWS credentials are configured correctly
   - Verify you have necessary AWS permissions
   - Review Terraform plan output for specific errors

4. **Tailscale Not Connecting**: 
   - Verify Tailscale auth key is valid and not expired
   - Check EC2 instance can reach Tailscale servers
   - Review container logs for Tailscale errors

5. **OpenVPN Issues**: 
   - Verify OpenVPN config file exists in correct location
   - Check OpenVPN configuration file format
   - Review container logs for OpenVPN errors

6. **Traffic Not Routing**: 
   - Verify routes are approved in Tailscale admin console
   - Check iptables rules are set correctly
   - Ensure IP forwarding is enabled

### Debugging Commands

```bash
# SSH into EC2 instance (use your key)
ssh -i ~/.ssh/your-key.pem ec2-user@<instance-ip>

# Check container logs
docker-compose logs tailscale
docker-compose logs openvpn

# Check iptables rules
iptables -L FORWARD -v
iptables -t nat -L POSTROUTING -v

# Monitor traffic
tcpdump -i tailscale0
tcpdump -i tun0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For issues and questions:
- Check the [Network Documentation](infra/docs/NETWORK.md) for detailed technical information
- Review [Tailscale Documentation](https://tailscale.com/kb/) for Tailscale-specific issues
- Open an issue in this repository for project-specific problems

## Related Documentation

- [Tailscale Subnet Routing](https://tailscale.com/kb/1019/subnets) - How to configure subnet routing
- [Tailscale Exit Nodes](https://tailscale.com/kb/1103/exit-nodes) - How to configure and use exit nodes
- [Tailscale Admin Console](https://login.tailscale.com/admin/machines) - Machine management interface
- [Network Architecture Guide](infra/docs/NETWORK.md) - Detailed network topology and iptables rules 