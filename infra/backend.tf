# Terraform Backend Configuration for Terraform Cloud

terraform {
  backend "remote" {
    # hostname will be set via environment variable TF_CLOUD_HOSTNAME or defaults to app.terraform.io
    # organization and workspace will be set via environment variables or CLI flags
  }

  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
