# Tailscale + OpenVPN Infrastructure

This CDKTF project deploys a VPN infrastructure using Tailscale and OpenVPN on AWS EC2.

## Project Structure

```
infra/
├── src/                    # CDKTF source code
│   ├── main.py            # Main application entry point
│   └── stacks/            # Stack definitions
│       └── vpn_stack.py   # VPN infrastructure stack
├── config/                # Configuration files
│   ├── environments/      # Environment-specific configs
│   │   ├── prod/
│   │   ├── non-prod/
│   │   └── platform/
│   └── templates/         # Template files
├── docker/               # Docker-related files
│   ├── compose/          # Docker compose files
│   ├── scripts/          # Entrypoint scripts
│   └── Dockerfiles/      # Dockerfiles
├── docs/                 # Documentation
│   └── NETWORK.md        # Network architecture guide
├── tests/                # Test files
├── .env.example          # Environment template
├── .gitignore
├── cdktf.json
├── Pipfile
└── README.md
```

## Prerequisites

- Python 3.8+
- pipenv
- AWS CLI configured
- Terraform Cloud account
- Tailscale account with auth keys

## Environment Variables

Create a `.env` file with the following variables:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_SESSION_TOKEN=your_aws_session_token
AWS_REGION=your_aws_region

# Terraform Cloud Configuration
TERRAFORM_ORGANIZATION=your_terraform_organization
TERRAFORM_WORKSPACE=your_terraform_workspace # e.g. tailscale-openvpn-me
SHORT_REGION=your_short_region # e.g. me

# Tailscale Configuration
TS_AUTH_KEY=your_tailscale_auth_key_1

# OpenVPN Configuration
OPENVPN_CONFIG_ENV=your_environment # e.g. prod
```

## Installation

1. Install dependencies:
   ```bash
   pipenv install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

## Usage

### Deploy Infrastructure

```bash
# Synthesize and deploy
python src/main.py
cdktf deploy
```

### Destroy Infrastructure

```bash
cdktf destroy
```

### View Status

```bash
cdktf diff
cdktf list
```

## Architecture

The infrastructure consists of:

1. **EC2 Instance**: Amazon Linux 2023 ARM64 instance
2. **Docker Services**:
   - Tailscale daemon for VPN connectivity
   - OpenVPN server for additional VPN access
3. **Network Configuration**: IP forwarding and iptables rules

For detailed network architecture and iptables rules explanation, see [Network Documentation](docs/NETWORK.md).

## Security

- All sensitive data is stored in environment variables
- OpenVPN configs are stored in `config/environments/`
- Docker containers run with minimal privileges where possible

## Troubleshooting

### Common Issues

1. **Environment Variables Missing**: Ensure all required variables are set in `.env`
2. **Docker Compose Issues**: Check container logs with `docker-compose logs`
3. **Network Issues**: Verify IP forwarding is enabled and iptables rules are correct

### Logs

- EC2 instance logs: Check CloudWatch logs
- Docker logs: `docker-compose logs <service>`
- CDKTF logs: Check console output during deployment

## Documentation

- [Network Architecture & iptables Rules](docs/NETWORK.md) - Detailed explanation of network topology and packet flow

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation for any changes
4. Use meaningful commit messages

## License

This project is licensed under the MIT License. 