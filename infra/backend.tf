# Terraform Backend Configuration for Terraform Cloud

terraform {
  cloud {
    # hostname defaults to app.terraform.io
    # organization and workspace MUST be set via environment variables:
    # - TF_CLOUD_ORGANIZATION: Your Terraform Cloud organization name
    # - TF_WORKSPACE: Your workspace name
    #
    # Example:
    #   export TF_CLOUD_ORGANIZATION="your-org"
    #   export TF_WORKSPACE="your-workspace"
    #   terraform init
  }

  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
