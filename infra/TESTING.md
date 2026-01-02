# Testing Guide

This document explains how to test the Terraform infrastructure both locally and in CI/CD.

## Prerequisites for Testing

- Terraform CLI installed (version 1.0+)
- AWS credentials configured
- Terraform Cloud account and token
- OpenVPN configuration file(s)
- Tailscale auth key

## Local Testing

### 1. Validation Testing (No AWS Credentials Required)

Test the Terraform syntax and configuration without deploying:

```bash
cd infra

# Format check
terraform fmt -check -recursive

# Initialize (backend disabled for local validation)
terraform init -backend=false

# Validate configuration
terraform validate
```

Using Makefile:
```bash
cd infra
make validate
```

### 2. Plan Testing (AWS Credentials Required)

Test that Terraform can generate a valid execution plan:

```bash
cd infra

# Set required variables (or use terraform.tfvars)
export TF_VAR_aws_region="us-east-1"
export TF_VAR_short_region="test"
export TF_VAR_ts_auth_key="test-key-for-validation"
export TF_VAR_openvpn_config_env="prod"

# Initialize with backend
terraform init \
  -backend-config="organization=your-org" \
  -backend-config="workspaces={name=\"your-workspace\"}"

# Generate plan
terraform plan
```

Using Makefile:
```bash
cd infra
make init
make plan
```

### 3. Local Deployment Testing

For testing in a safe environment:

```bash
cd infra

# Create a test workspace in Terraform Cloud
terraform workspace new test-environment

# Review the plan
terraform plan -out=tfplan

# Apply if plan looks good
terraform apply tfplan

# Test the infrastructure
# ... run your tests ...

# Destroy when done
terraform destroy
```

### 4. Configuration File Testing

Verify all configuration files are present and valid:

```bash
cd infra

# Check OpenVPN configs exist
ls -la config/environments/prod/config.ovpn
ls -la config/environments/non-prod/config.ovpn

# Check Docker configs
ls -la docker/compose/
ls -la docker/scripts/
ls -la docker/Dockerfiles/

# Check templates
ls -la config/templates/
```

### 5. Template Testing

Test the user_data template rendering:

```bash
cd infra

# Use terraform console to test template
terraform console
> templatefile("${path.module}/user_data.sh.tpl", {
    tailscale_docker_compose_content = "test",
    tailscale_env_content = "test",
    openvpn_config = "test",
    ts_ovpn_docker_compose_content = "test",
    openvpn_ts_env_content = "test",
    openvpn_dockerfile_content = "test",
    tailscale_entrypoint_content = "test"
  })
```

## CI/CD Testing

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/terraform.yml`) that automatically:

1. **On Pull Requests:**
   - Checks Terraform formatting
   - Initializes Terraform
   - Validates configuration
   - Generates and comments the plan on the PR

2. **On Main Branch Push:**
   - Performs all PR checks
   - Automatically applies changes

#### Required Secrets

Configure these in GitHub repository settings:

- `TF_API_TOKEN` - Terraform Cloud API token
- `TF_CLOUD_ORGANIZATION` - Terraform Cloud organization name
- `TF_WORKSPACE` - Terraform Cloud workspace name
- `AWS_REGION` - AWS region for deployment
- `SHORT_REGION` - Short region identifier
- `TS_AUTH_KEY` - Tailscale authentication key
- `OPENVPN_CONFIG_ENV` - OpenVPN environment (prod/non-prod)
- `AWS_KEY_NAME` - AWS SSH key pair name

#### Testing the CI/CD Pipeline

1. Create a feature branch
2. Make changes to infrastructure code
3. Push and create a Pull Request
4. Review the Terraform plan in PR comments
5. Merge to main to apply changes

### Manual CI/CD Testing

To test CI/CD locally using GitHub Actions:

```bash
# Install act (GitHub Actions local runner)
# https://github.com/nektos/act

# Test the workflow
act pull_request -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Or test specific jobs
act -j terraform
```

## Integration Testing

After deployment, test the infrastructure:

### 1. EC2 Instance Testing

```bash
# Get instance IP from Terraform output
terraform output instance_public_ip

# SSH into instance
ssh -i ~/.ssh/your-key.pem ec2-user@<instance-ip>

# Check Docker is running
sudo systemctl status docker

# Check containers are running
docker ps

# Should see:
# - ts-ovpn-tailscale-1
# - ts-ovpn-openvpn-1
# - ts-tailscale-1
```

### 2. Container Health Testing

```bash
# SSH into EC2 instance first

# Check tailscale container logs
docker logs ts-ovpn-tailscale-1

# Check openvpn container logs
docker logs ts-ovpn-openvpn-1

# Verify Tailscale is connected
docker exec ts-ovpn-tailscale-1 tailscale status

# Test OpenVPN connection
docker exec ts-ovpn-openvpn-1 curl -I https://google.com
```

### 3. Network Testing

```bash
# SSH into EC2 instance

# Verify IP forwarding is enabled
sysctl net.ipv4.ip_forward
# Should output: net.ipv4.ip_forward = 1

# Check iptables rules
sudo iptables -L FORWARD -v
sudo iptables -t nat -L POSTROUTING -v

# Monitor traffic (optional)
sudo tcpdump -i tailscale0
sudo tcpdump -i tun0
```

### 4. Tailscale Integration Testing

From your Tailscale client machine:

```bash
# Check Tailscale status
tailscale status

# Should see the gateway machine listed

# Test connectivity to gateway
ping <gateway-tailscale-ip>

# Test routing through gateway
# (requires approved routes in Tailscale admin)
ping <corporate-resource-ip>
```

### 5. End-to-End Testing

Complete workflow test:

```bash
# 1. Deploy infrastructure
cd infra
terraform apply -auto-approve

# 2. Wait for deployment (5-10 minutes)
# Monitor via AWS Console or:
aws ec2 describe-instances --filters "Name=tag:Name,Values=TunnelOpenVPN-*"

# 3. Verify Tailscale registration
# Go to https://login.tailscale.com/admin/machines
# Verify gateway machine appears

# 4. Approve routes in Tailscale admin

# 5. Test from client
tailscale up --accept-routes
ping <corporate-resource-ip>

# 6. Cleanup (optional)
cd infra
terraform destroy -auto-approve
```

## Test Checklist

Before considering the migration complete:

- [ ] Terraform validation passes (`terraform validate`)
- [ ] Terraform formatting is correct (`terraform fmt -check`)
- [ ] Terraform plan generates without errors
- [ ] All required configuration files are present
- [ ] Backend configuration works with Terraform Cloud
- [ ] CI/CD workflow runs successfully
- [ ] EC2 instance deploys correctly
- [ ] Docker containers start and run
- [ ] Tailscale connects successfully
- [ ] OpenVPN connects successfully
- [ ] iptables rules are configured
- [ ] IP forwarding is enabled
- [ ] Network routing works end-to-end
- [ ] Documentation is complete and accurate

## Troubleshooting Tests

### Test Fails: Terraform Init

**Symptoms:** `terraform init` fails with backend errors

**Solutions:**
```bash
# Check Terraform Cloud token
terraform login

# Verify organization/workspace exist
# Check at https://app.terraform.io/

# Try with explicit backend config
terraform init \
  -backend-config="organization=YOUR_ORG" \
  -backend-config="workspaces={name=\"YOUR_WORKSPACE\"}"
```

### Test Fails: Terraform Validate

**Symptoms:** Validation errors about missing files or invalid configuration

**Solutions:**
```bash
# Ensure in correct directory
cd infra

# Check all files are present
ls -la *.tf

# Check file syntax
terraform fmt -recursive
terraform validate
```

### Test Fails: Terraform Plan

**Symptoms:** Plan fails with variable or provider errors

**Solutions:**
```bash
# Check variables are set
echo $TF_VAR_aws_region
echo $TF_VAR_ts_auth_key

# Or create terraform.tfvars
cat > terraform.tfvars << EOF
aws_region = "us-east-1"
short_region = "us"
ts_auth_key = "your-key"
openvpn_config_env = "prod"
EOF

# Check AWS credentials
aws sts get-caller-identity
```

### Test Fails: Deployment

**Symptoms:** Apply fails during deployment

**Solutions:**
```bash
# Check AWS permissions
aws ec2 describe-instances --region us-east-1

# Review Terraform error messages
terraform apply

# Enable detailed logging
export TF_LOG=DEBUG
terraform apply
```

## Automated Testing Scripts

For automated testing, use these scripts:

### Quick Validation Script

```bash
#!/bin/bash
set -e

cd infra

echo "Testing Terraform configuration..."

# Format check
echo "1. Checking formatting..."
terraform fmt -check -recursive

# Validation
echo "2. Validating configuration..."
terraform init -backend=false
terraform validate

echo "✓ All tests passed!"
```

### Full Test Script

```bash
#!/bin/bash
set -e

cd infra

echo "Running full Terraform test suite..."

# Format
terraform fmt -check -recursive

# Init
terraform init

# Validate
terraform validate

# Plan
terraform plan -out=tfplan

echo "✓ Full test suite passed!"
echo "Review the plan above before applying."
```

## Performance Testing

### Deployment Time

Expected deployment times:
- Terraform init: 10-30 seconds
- Terraform plan: 5-15 seconds
- Terraform apply: 5-10 minutes (EC2 instance creation + user_data execution)

### Infrastructure Cost

Estimated monthly costs (us-east-1, as of January 2026):
- t4g.nano EC2 instance: ~$3-4/month
- Data transfer: Variable (depends on usage)
- Total: ~$5-10/month

**Note:** Pricing is subject to change. Use the [AWS Pricing Calculator](https://calculator.aws/) for current estimates in your region.

## Continuous Testing

Recommended testing schedule:

1. **On every commit:** Format check, validation
2. **On every PR:** Format, validation, plan
3. **On merge to main:** Full deployment to test environment
4. **Weekly:** Full end-to-end test in production
5. **Monthly:** Review and update test procedures

## Conclusion

This testing guide ensures the Terraform infrastructure is:
- Syntactically correct
- Functionally working
- Properly integrated
- Well documented
- Ready for production use

For questions or issues, refer to the [MIGRATION.md](../MIGRATION.md) guide or open an issue.
