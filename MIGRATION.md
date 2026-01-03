# Migration Guide: CDKTF to Vanilla Terraform

This guide explains how to migrate from the deprecated CDKTF setup to vanilla Terraform.

## Overview

This project has been migrated from CDK for Terraform (CDKTF) to vanilla Terraform because CDKTF is now deprecated and unsupported. The infrastructure functionality remains identical, but the tooling and workflow have changed.

## What Changed

### Before (CDKTF)
- Infrastructure defined in Python (`infra/src/`)
- Required Python, pipenv, and CDKTF CLI
- Deployment: `cdktf deploy`
- Configuration: Python code + environment variables

### After (Vanilla Terraform)
- Infrastructure defined in HCL (`.tf` files in `infra/`)
- Required only Terraform CLI
- Deployment: `terraform apply`
- Configuration: `.tfvars` files + environment variables

## Migration Steps for Existing Users

### 1. Install Terraform

If you don't have Terraform installed:

```bash
# macOS
brew install terraform

# Linux (Ubuntu/Debian)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Or download directly from https://www.terraform.io/downloads
```

### 2. Update Your Environment

You no longer need:
- Python virtual environment (`pipenv shell`)
- CDKTF CLI
- Devbox (unless you prefer it for other tools)

### 3. Configure Variables

Create `infra/terraform.tfvars` from the example:

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

### 4. Configure Backend (Terraform Cloud)

The backend configuration is in `backend.tf`. You need to configure your Terraform Cloud credentials:

**Option A: Using Terraform Cloud Token**
```bash
terraform login
```

**Option B: Using Environment Variables**
```bash
export TF_CLOUD_ORGANIZATION="your-org"
export TF_WORKSPACE="your-workspace"
export TF_TOKEN_app_terraform_io="your-token"
```

### 5. Initialize and Deploy

```bash
cd infra

# Set Terraform Cloud configuration
export TF_CLOUD_ORGANIZATION="your-org"
export TF_WORKSPACE="your-workspace"

# Initialize Terraform (first time only)
terraform init

# Review planned changes
terraform plan

# Apply changes
terraform apply
```

## Command Equivalence

| CDKTF Command | Terraform Command |
|---------------|-------------------|
| `cdktf deploy` | `terraform apply` |
| `cdktf plan` | `terraform plan` |
| `cdktf destroy` | `terraform destroy` |
| `cdktf diff` | `terraform plan` |
| `cdktf list` | `terraform state list` |
| `cdktf synth` | (not needed) |

## Using the Makefile

A Makefile has been provided for convenience:

```bash
# Show available commands
make help

# Initialize Terraform
make init

# Validate configuration
make validate

# Plan changes
make plan

# Apply changes
make apply

# Destroy infrastructure
make destroy

# Format code
make fmt
```

## Configuration Files Mapping

| CDKTF Files | Terraform Files |
|-------------|-----------------|
| `src/main.py` | `providers.tf`, `backend.tf` |
| `src/stacks/vpn_stack.py` | `ec2.tf`, `data.tf`, `locals.tf` |
| `cdktf.json` | (removed, not needed) |
| Environment variables | `variables.tf`, `terraform.tfvars` |

## State Management

Your Terraform state remains in Terraform Cloud. The new configuration uses the same backend, so your existing infrastructure state will be preserved.

**Important:** Make sure to use the same organization and workspace names when initializing.

## Environment Variables

The following environment variables are now defined as Terraform variables:

| Environment Variable (Old) | Terraform Variable (New) |
|----------------------------|--------------------------|
| `AWS_REGION` | `var.aws_region` |
| `SHORT_REGION` | `var.short_region` |
| `TS_AUTH_KEY` | `var.ts_auth_key` |
| `OPENVPN_CONFIG_ENV` | `var.openvpn_config_env` |

AWS credentials can still be provided via environment variables or AWS CLI configuration.

## CI/CD Changes

If you're using CI/CD, update your pipelines to use Terraform commands instead of CDKTF:

### GitHub Actions
A new workflow has been provided at `.github/workflows/terraform.yml`. Configure the following secrets:
- `TF_API_TOKEN`
- `TF_CLOUD_ORGANIZATION`
- `TF_WORKSPACE`
- `AWS_REGION`
- `SHORT_REGION`
- `TS_AUTH_KEY`
- `OPENVPN_CONFIG_ENV`
- `AWS_KEY_NAME`

### Other CI/CD Systems
Replace `cdktf` commands with `terraform` commands and ensure Terraform CLI is installed in your CI environment.

## Troubleshooting

### Issue: Backend initialization fails
**Solution:** Ensure environment variables are set correctly:
```bash
export TF_CLOUD_ORGANIZATION="YOUR_ORG"
export TF_WORKSPACE="YOUR_WORKSPACE"
terraform init
```

### Issue: Variable not found
**Solution:** Ensure you've created `terraform.tfvars` with all required variables, or pass them via command line:
```bash
terraform apply -var="aws_region=me-central-1" -var="ts_auth_key=xxx"
```

### Issue: State conflicts
**Solution:** If you have existing CDKTF state, you may need to import resources or migrate state. Contact your team lead before proceeding.

## Benefits of Migration

1. **Simpler Setup**: No Python dependencies, just Terraform CLI
2. **Industry Standard**: Terraform HCL is the standard for IaC
3. **Better IDE Support**: More tools support native Terraform
4. **Faster Execution**: No Python runtime overhead
5. **Active Support**: Terraform is actively maintained by HashiCorp
6. **Better Documentation**: Extensive Terraform documentation and community

## Getting Help

- **Terraform Documentation**: https://www.terraform.io/docs
- **Terraform Cloud**: https://cloud.hashicorp.com/products/terraform
- **Repository Issues**: Open an issue in this repository

## Rollback

If you need to rollback to CDKTF (not recommended):
1. Checkout the commit before this migration
2. Ensure CDKTF and Python dependencies are installed
3. Use `cdktf` commands as before

However, we strongly recommend completing the migration to Terraform as CDKTF is deprecated.
