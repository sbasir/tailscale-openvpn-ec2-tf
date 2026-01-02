#!/bin/bash
# Test script for Terraform configuration
# Usage: ./test.sh [quick|full]

set -e

MODE="${1:-quick}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Terraform Configuration Test Suite"
echo "Mode: $MODE"
echo "Directory: $SCRIPT_DIR"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: Check required files
echo "📋 Test 1: Checking required files..."
required_files=(
    "variables.tf"
    "providers.tf"
    "backend.tf"
    "data.tf"
    "locals.tf"
    "ec2.tf"
    "outputs.tf"
    "user_data.sh.tpl"
    "terraform.tfvars.example"
    "Makefile"
)

for file in "${required_files[@]}"; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
        success "Found $file"
    else
        error "Missing $file"
    fi
done
echo ""

# Test 2: Check configuration directories
echo "📁 Test 2: Checking configuration directories..."
required_dirs=(
    "config/environments"
    "config/templates"
    "docker/compose"
    "docker/scripts"
    "docker/Dockerfiles"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$SCRIPT_DIR/$dir" ]]; then
        success "Found $dir"
    else
        error "Missing $dir"
    fi
done
echo ""

# Test 3: Terraform format check
echo "🎨 Test 3: Checking Terraform formatting..."
if terraform fmt -check -recursive; then
    success "Terraform files are properly formatted"
else
    warning "Terraform files need formatting. Run: terraform fmt -recursive"
fi
echo ""

# Test 4: Terraform initialization (without backend)
echo "⚙️  Test 4: Initializing Terraform (backend disabled)..."
if terraform init -backend=false > /dev/null 2>&1; then
    success "Terraform initialized successfully"
else
    error "Terraform initialization failed"
fi
echo ""

# Test 5: Terraform validation
echo "✅ Test 5: Validating Terraform configuration..."
if terraform validate > /dev/null 2>&1; then
    success "Terraform configuration is valid"
else
    error "Terraform validation failed"
fi
echo ""

# Full mode tests
if [[ "$MODE" == "full" ]]; then
    echo "🔬 Running additional tests in full mode..."
    echo ""
    
    # Test 6: Check for OpenVPN configs
    echo "📦 Test 6: Checking OpenVPN configurations..."
    if [[ -f "$SCRIPT_DIR/config/environments/prod/config.ovpn" ]]; then
        success "Production OpenVPN config found"
    else
        warning "Production OpenVPN config not found (required for deployment)"
    fi
    
    if [[ -f "$SCRIPT_DIR/config/environments/non-prod/config.ovpn" ]]; then
        success "Non-production OpenVPN config found"
    else
        warning "Non-production OpenVPN config not found (optional)"
    fi
    echo ""
    
    # Test 7: Check environment variables
    echo "🔐 Test 7: Checking environment variables..."
    required_vars=(
        "TF_VAR_aws_region"
        "TF_VAR_short_region"
        "TF_VAR_ts_auth_key"
        "TF_VAR_openvpn_config_env"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
            warning "Environment variable $var is not set"
        else
            success "Environment variable $var is set"
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        echo ""
        warning "Some required variables are not set. They can be provided via:"
        echo "  - Environment variables (TF_VAR_*)"
        echo "  - terraform.tfvars file"
        echo "  - Command line (-var flags)"
    fi
    echo ""
    
    # Test 8: Terraform plan (if credentials available)
    echo "📊 Test 8: Generating Terraform plan..."
    if [[ -n "${TF_VAR_aws_region}" && -n "${TF_VAR_ts_auth_key}" ]]; then
        # Check if backend is configured
        if terraform init > /dev/null 2>&1; then
            if terraform plan -input=false > /dev/null 2>&1; then
                success "Terraform plan generated successfully"
            else
                warning "Terraform plan failed (may need AWS credentials or backend configuration)"
            fi
        else
            warning "Cannot generate plan without backend configuration"
        fi
    else
        warning "Skipping plan test (missing required variables)"
    fi
    echo ""
fi

# Summary
echo "═══════════════════════════════════════"
echo "🎉 Test suite completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Create terraform.tfvars with your configuration"
echo "  2. Run: terraform init"
echo "  3. Run: terraform plan"
echo "  4. Run: terraform apply"
echo ""
echo "For detailed testing guide, see: TESTING.md"
echo "═══════════════════════════════════════"
