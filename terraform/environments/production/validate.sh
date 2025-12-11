#!/bin/bash

# BARQ Fleet Management - Production Configuration Validator
# This script validates the production Terraform configuration before deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track validation status
VALIDATION_FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BARQ Fleet Management - Production Validation                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Helper functions
print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    VALIDATION_FAILED=1
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 1. Check prerequisites
echo -e "\n${BLUE}═══ Checking Prerequisites ═══${NC}\n"

print_check "Terraform installed..."
if command -v terraform &> /dev/null; then
    version=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)
    if [[ "$(printf '%s\n' "1.0.0" "$version" | sort -V | head -n1)" == "1.0.0" ]]; then
        print_success "Terraform $version installed"
    else
        print_error "Terraform version $version is too old (required: >= 1.0.0)"
    fi
else
    print_error "Terraform is not installed"
fi

print_check "Google Cloud SDK installed..."
if command -v gcloud &> /dev/null; then
    version=$(gcloud version --format="value(core)" 2>/dev/null)
    print_success "Google Cloud SDK $version installed"
else
    print_error "Google Cloud SDK is not installed"
fi

print_check "Google Cloud authentication..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    print_success "Authenticated as: $account"
else
    print_error "Not authenticated with Google Cloud"
fi

print_check "Project configuration..."
current_project=$(gcloud config get-value project 2>/dev/null)
if [[ -n "$current_project" ]]; then
    print_success "Current project: $current_project"
else
    print_warning "No default project set"
fi

# 2. Check Terraform configuration
echo -e "\n${BLUE}═══ Checking Terraform Configuration ═══${NC}\n"

print_check "Terraform files exist..."
if [[ -f "main.tf" ]] && [[ -f "variables.tf" ]] && [[ -f "outputs.tf" ]]; then
    print_success "All required Terraform files found"
else
    print_error "Missing Terraform files (main.tf, variables.tf, or outputs.tf)"
fi

print_check "terraform.tfvars exists..."
if [[ -f "terraform.tfvars" ]]; then
    print_success "terraform.tfvars found"
else
    print_warning "terraform.tfvars not found (using defaults or environment variables)"
    if [[ -f "terraform.tfvars.example" ]]; then
        print_info "Run: cp terraform.tfvars.example terraform.tfvars"
    fi
fi

print_check "Terraform syntax..."
if terraform fmt -check &> /dev/null; then
    print_success "Terraform syntax is properly formatted"
else
    print_warning "Terraform files need formatting (run: terraform fmt)"
fi

print_check "Terraform validation..."
if terraform validate &> /dev/null; then
    print_success "Terraform configuration is valid"
else
    print_error "Terraform validation failed"
    terraform validate
fi

# 3. Check GCS backend bucket
echo -e "\n${BLUE}═══ Checking Terraform State Backend ═══${NC}\n"

print_check "Terraform backend configuration..."
backend_bucket=$(grep -A 3 'backend "gcs"' main.tf | grep bucket | cut -d'"' -f2)
if [[ -n "$backend_bucket" ]]; then
    print_success "Backend bucket: $backend_bucket"

    print_check "Backend bucket exists..."
    if gsutil ls "gs://$backend_bucket" &> /dev/null; then
        print_success "Backend bucket exists and is accessible"

        # Check versioning
        versioning=$(gsutil versioning get "gs://$backend_bucket" 2>/dev/null | grep Enabled || echo "")
        if [[ -n "$versioning" ]]; then
            print_success "Bucket versioning is enabled"
        else
            print_warning "Bucket versioning is not enabled (recommended for state protection)"
            print_info "Run: gsutil versioning set on gs://$backend_bucket"
        fi
    else
        print_error "Backend bucket does not exist or is not accessible"
        print_info "Run: gsutil mb -p PROJECT_ID -l me-central1 gs://$backend_bucket"
    fi
else
    print_error "Could not find backend bucket configuration"
fi

# 4. Check required variables
echo -e "\n${BLUE}═══ Checking Required Variables ═══${NC}\n"

required_vars=(
    "project_id"
    "region"
    "db_user"
    "db_password"
    "database_url"
    "secret_key"
    "google_client_id"
    "google_client_secret"
    "alert_email"
)

if [[ -f "terraform.tfvars" ]]; then
    for var in "${required_vars[@]}"; do
        print_check "Variable: $var..."
        if grep -q "^$var\s*=" terraform.tfvars; then
            value=$(grep "^$var\s*=" terraform.tfvars | cut -d'=' -f2 | tr -d ' "')

            # Check for placeholder values
            if [[ "$value" =~ REPLACE|YOUR_|EXAMPLE|CHANGEME|TODO ]]; then
                print_error "$var contains placeholder value"
            elif [[ "$var" == "db_password" || "$var" == "secret_key" ]] && [[ ${#value} -lt 16 ]]; then
                print_error "$var is too short (should be >= 16 characters)"
            elif [[ "$var" == "alert_email" ]] && ! [[ "$value" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                print_error "$var is not a valid email address"
            else
                # Mask sensitive values
                if [[ "$var" =~ password|secret|dsn|webhook ]]; then
                    print_success "$var = [REDACTED]"
                else
                    print_success "$var = $value"
                fi
            fi
        else
            if [[ -z "${!var}" ]]; then
                print_error "$var is not set in terraform.tfvars or environment"
            else
                print_success "$var set via environment variable"
            fi
        fi
    done
else
    print_warning "terraform.tfvars not found, checking environment variables..."
    for var in "${required_vars[@]}"; do
        env_var="TF_VAR_$var"
        if [[ -n "${!env_var}" ]]; then
            print_success "$var set via $env_var"
        else
            print_error "$var is not set"
        fi
    done
fi

# 5. Check GCP resources
echo -e "\n${BLUE}═══ Checking GCP Resources ═══${NC}\n"

if [[ -f "terraform.tfvars" ]]; then
    project_id=$(grep "^project_id\s*=" terraform.tfvars | cut -d'=' -f2 | tr -d ' "')
    region=$(grep "^region\s*=" terraform.tfvars | cut -d'=' -f2 | tr -d ' "')
elif [[ -n "$TF_VAR_project_id" ]]; then
    project_id="$TF_VAR_project_id"
    region="${TF_VAR_region:-me-central1}"
else
    project_id="$current_project"
    region="me-central1"
fi

if [[ -n "$project_id" ]]; then
    print_check "GCP project '$project_id' exists..."
    if gcloud projects describe "$project_id" &> /dev/null; then
        print_success "Project exists"

        print_check "Billing enabled..."
        billing_account=$(gcloud beta billing projects describe "$project_id" --format="value(billingAccountName)" 2>/dev/null)
        if [[ -n "$billing_account" ]]; then
            print_success "Billing is enabled"
        else
            print_error "Billing is not enabled for this project"
        fi

        print_check "Required APIs..."
        required_apis=(
            "run.googleapis.com"
            "secretmanager.googleapis.com"
            "sqladmin.googleapis.com"
            "compute.googleapis.com"
            "vpcaccess.googleapis.com"
            "servicenetworking.googleapis.com"
            "monitoring.googleapis.com"
        )

        enabled_apis=$(gcloud services list --enabled --project="$project_id" --format="value(name)" 2>/dev/null)

        for api in "${required_apis[@]}"; do
            if echo "$enabled_apis" | grep -q "$api"; then
                print_success "$api is enabled"
            else
                print_warning "$api is not enabled (will be enabled by Terraform)"
            fi
        done
    else
        print_error "Project '$project_id' does not exist or is not accessible"
    fi
else
    print_error "Could not determine project_id"
fi

# 6. Check security configurations
echo -e "\n${BLUE}═══ Checking Security Configuration ═══${NC}\n"

print_check "Checking for hardcoded secrets in Terraform files..."
if grep -r -E "(password|secret|key)\s*=\s*\"[^$]" *.tf 2>/dev/null | grep -v "secret_id" | grep -v "example" | grep -v "description"; then
    print_error "Found potential hardcoded secrets in Terraform files"
else
    print_success "No hardcoded secrets found"
fi

print_check "Deletion protection..."
if grep -q 'deletion_protection.*=.*true' main.tf; then
    print_success "Deletion protection is enabled for Cloud SQL"
else
    print_warning "Deletion protection is not enabled (recommended for production)"
fi

print_check "High availability configuration..."
if grep -q 'availability_type.*=.*"REGIONAL"' main.tf; then
    print_success "Cloud SQL is configured for high availability"
else
    print_warning "Cloud SQL is not configured for high availability"
fi

print_check "Private IP configuration..."
if grep -q 'ipv4_enabled.*=.*false' main.tf; then
    print_success "Cloud SQL is configured with private IP only"
else
    print_error "Cloud SQL may be using public IP (security risk)"
fi

print_check "Minimum instances for HA..."
min_instances=$(grep -o 'minScale".*=.*"[0-9]*"' main.tf | head -1 | grep -o '[0-9]*')
if [[ "$min_instances" -ge 2 ]]; then
    print_success "Minimum instances set to $min_instances (high availability)"
else
    print_warning "Minimum instances set to $min_instances (consider >= 2 for HA)"
fi

# 7. Cost estimation
echo -e "\n${BLUE}═══ Estimated Monthly Costs ═══${NC}\n"

print_info "Cost breakdown (approximate):"
echo "  - Cloud Run (API):      \$150-\$800  (2-50 instances, 4vCPU, 4GB)"
echo "  - Cloud Run (Web):      \$50-\$200   (2-20 instances, 2vCPU, 1GB)"
echo "  - Cloud SQL:            \$400-\$500  (db-custom-4-15360, HA)"
echo "  - VPC Connector:        \$30-\$100   (300-1000 Mbps)"
echo "  - Secret Manager:       \$1-\$5      (10 secrets)"
echo "  - Monitoring & Logging: \$10-\$20    (standard metrics)"
echo "  - Cloud Armor:          \$5          (1 policy)"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TOTAL (estimated):      \$650-\$1,630/month"
echo ""
print_warning "Set up budget alerts to monitor actual costs!"

# 8. Deployment readiness
echo -e "\n${BLUE}═══ Deployment Readiness Checklist ═══${NC}\n"

checklist=(
    "Terraform installed and version >= 1.0.0"
    "Google Cloud SDK installed and authenticated"
    "GCP project exists and billing is enabled"
    "terraform.tfvars created with actual values"
    "All required variables set (no placeholders)"
    "Backend bucket exists with versioning enabled"
    "Strong passwords generated (>= 32 characters)"
    "Google OAuth credentials configured"
    "Sentry project created (if using error tracking)"
    "Alert email and Slack webhook configured"
    "Domain names registered (if using custom domains)"
    "DNS provider access configured"
    "Backup and disaster recovery plan documented"
    "Security audit completed"
    "Team notified of deployment"
)

all_ready=true
for item in "${checklist[@]}"; do
    # This is a manual checklist - just display it
    echo "  [ ] $item"
done

# Summary
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Validation Summary                                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ $VALIDATION_FAILED -eq 0 ]]; then
    print_success "All automated checks passed!"
    echo ""
    print_info "Next steps:"
    echo "  1. Review the deployment checklist above"
    echo "  2. Ensure all items are completed"
    echo "  3. Run: terraform plan"
    echo "  4. Review the plan carefully"
    echo "  5. Run: terraform apply"
    echo ""
    exit 0
else
    print_error "Validation failed! Please fix the errors above before deploying."
    echo ""
    print_info "Common fixes:"
    echo "  - Install missing tools: brew install terraform google-cloud-sdk"
    echo "  - Authenticate: gcloud auth login && gcloud auth application-default login"
    echo "  - Create terraform.tfvars: cp terraform.tfvars.example terraform.tfvars"
    echo "  - Replace placeholder values in terraform.tfvars"
    echo "  - Enable billing: https://console.cloud.google.com/billing"
    echo ""
    exit 1
fi
