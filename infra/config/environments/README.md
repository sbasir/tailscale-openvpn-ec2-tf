# OpenVPN Configuration Environments

This directory contains OpenVPN configuration files for different environments.

## Structure

```
environments/
├── prod/
│   └── config.ovpn          # Production OpenVPN configuration
└── non-prod/
    └── config.ovpn          # Non-production OpenVPN configuration
```

## Setup

1. Copy your OpenVPN configuration file to the appropriate environment directory
2. Rename it to `config.ovpn`
3. Ensure it includes all necessary certificates, keys, and routing information

## Example

```bash
# For production environment
cp ~/Downloads/my-vpn-config.ovpn infra/config/environments/prod/config.ovpn

# For non-production environment
cp ~/Downloads/my-test-vpn-config.ovpn infra/config/environments/non-prod/config.ovpn
```

## Security Notes

- **DO NOT** commit actual OpenVPN configuration files to version control
- Configuration files often contain sensitive certificates and keys
- Use `.gitignore` to exclude `*.ovpn` files (already configured)
- Keep your configuration files secure and encrypted at rest

## Configuration Requirements

Your OpenVPN configuration should:
- Be a valid OpenVPN client configuration
- Include all necessary certificates inline or reference them correctly
- Have proper routing configured for your corporate network
- Use compatible cipher and authentication settings

## Validation

To validate your OpenVPN configuration:

```bash
# Test locally with OpenVPN
openvpn --config config/environments/prod/config.ovpn

# Or test in a container
docker run -it --rm --cap-add=NET_ADMIN --device /dev/net/tun \
  -v $(pwd)/config/environments/prod/config.ovpn:/config.ovpn:ro \
  debian:bookworm-slim /bin/bash -c \
  "apt-get update && apt-get install -y openvpn && openvpn --config /config.ovpn"
```

## Troubleshooting

If OpenVPN fails to connect:
1. Check that all referenced files (ca.crt, client.crt, client.key) are included inline or accessible
2. Verify server address and port are correct
3. Ensure your network allows outbound connections to the VPN server
4. Review OpenVPN logs for specific error messages
5. Consult your VPN provider's documentation
