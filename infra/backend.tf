# Terraform Backend Configuration for Terraform Cloud

terraform {
  cloud {
    # hostname defaults to app.terraform.io
    # organization and workspace can be set via:
    # 1. TF_CLOUD_ORGANIZATION and TF_WORKSPACE environment variables
    # 2. terraform.tfvars or *.auto.tfvars files
    # 3. -backend-config flags during terraform init
  }

  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
