# Makefile for Terraform operations

.PHONY: help init validate plan apply destroy fmt lint clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize Terraform
	terraform init

validate: ## Validate Terraform configuration
	terraform fmt -check
	terraform validate

plan: ## Show Terraform plan
	terraform plan

apply: ## Apply Terraform configuration
	terraform apply

destroy: ## Destroy Terraform infrastructure
	terraform destroy

fmt: ## Format Terraform files
	terraform fmt -recursive

lint: validate ## Lint Terraform configuration (alias for validate)

clean: ## Clean up Terraform files
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate
	rm -f terraform.tfstate.backup

test: validate ## Run tests (validate configuration)
	@echo "Running Terraform validation..."
	@terraform validate
	@echo "✓ Terraform configuration is valid"
