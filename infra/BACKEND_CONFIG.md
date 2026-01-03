# Terraform Cloud Backend Configuration Guide

## Overview

This project uses Terraform Cloud for remote state management. The backend is configured using the `cloud` block (available in Terraform 1.1+), which is the modern and recommended approach.

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set these environment variables before running `terraform init`:

```bash
export TF_CLOUD_ORGANIZATION="your-organization"
export TF_WORKSPACE="your-workspace"
export TF_TOKEN_app_terraform_io="your-terraform-cloud-token"
```

Then simply run:
```bash
terraform init
```

### Method 2: Terraform Login

Authenticate interactively:
```bash
terraform login
```

This will prompt you to create a token and save it automatically. Then set your organization and workspace:

```bash
export TF_CLOUD_ORGANIZATION="your-organization"
export TF_WORKSPACE="your-workspace"
terraform init
```

### Method 3: Configuration File

Create a `.terraformrc` or `terraform.rc` file in your home directory:

```hcl
credentials "app.terraform.io" {
  token = "your-terraform-cloud-token"
}
```

Then set environment variables for organization and workspace as shown in Method 1.

## Why Not Use -backend-config?

The older `-backend-config` command-line arguments do not work with the `cloud` block. The error you'll see is:

```
Error: Invalid backend configuration argument

The backend configuration argument "workspaces" given on the command line is 
not expected for the selected backend type.
```

This is because:
- The `cloud` block uses environment variables (`TF_CLOUD_ORGANIZATION`, `TF_WORKSPACE`)
- The old `remote` backend used different configuration syntax
- The `cloud` block is the modern approach for Terraform Cloud (1.1+)

## CI/CD Configuration

For GitHub Actions, set these repository secrets:
- `TF_API_TOKEN` - Your Terraform Cloud API token
- `TF_CLOUD_ORGANIZATION` - Your organization name
- `TF_WORKSPACE` - Your workspace name

The workflow will automatically use these via environment variables.

## Troubleshooting

### Error: Backend initialization fails

**Problem:** Organization or workspace not found

**Solution:**
1. Verify your organization exists at https://app.terraform.io/
2. Verify your workspace exists within that organization
3. Check that environment variables are set correctly:
   ```bash
   echo $TF_CLOUD_ORGANIZATION
   echo $TF_WORKSPACE
   ```

### Error: Invalid credentials

**Problem:** Authentication failed

**Solution:**
1. Run `terraform login` to authenticate
2. Or verify your token is correct in `~/.terraform.d/credentials.tfrc.json`
3. Or set `TF_TOKEN_app_terraform_io` environment variable

### Switching Workspaces

To switch between workspaces:

```bash
export TF_WORKSPACE="different-workspace"
terraform init -reconfigure
```

## Migration from `remote` Backend

If you were using the older `remote` backend with `-backend-config` arguments, you need to:

1. Update `backend.tf` to use `cloud` block (already done)
2. Use environment variables instead of `-backend-config`
3. Re-run `terraform init`

The state will remain in Terraform Cloud - no migration needed.

## References

- [Terraform Cloud Configuration](https://developer.hashicorp.com/terraform/cli/cloud/settings)
- [Terraform Cloud Block](https://developer.hashicorp.com/terraform/language/settings/terraform-cloud)
- [Migrating from Remote Backend](https://developer.hashicorp.com/terraform/cli/cloud/migrating)
