#!/bin/bash

# ================================================================
# BARQ Fleet Management - GCP Deployment Setup
# ================================================================
# This script sets up all necessary GCP resources for deployment
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Project owner permissions on the GCP project
#
# Usage: ./setup-gcp.sh
# ================================================================

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-barqdps}"
REGION="${GCP_REGION:-me-central1}"
REPOSITORY_NAME="barq-fleet"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo ""
echo "=============================================="
echo "  BARQ Fleet Management - GCP Setup"
echo "=============================================="
echo "  Project: ${PROJECT_ID}"
echo "  Region: ${REGION}"
echo "=============================================="
echo ""

# Set the project
gcloud config set project "${PROJECT_ID}"

# ================================================================
# STEP 1: Enable required APIs
# ================================================================
log_step "1/7 Enabling required APIs..."

APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "iam.googleapis.com"
)

for api in "${APIS[@]}"; do
    log_info "Enabling ${api}..."
    gcloud services enable "${api}" --project="${PROJECT_ID}" --quiet || true
done

log_info "✅ APIs enabled"

# ================================================================
# STEP 2: Create Artifact Registry repository (if not exists)
# ================================================================
log_step "2/7 Setting up Artifact Registry..."

if gcloud artifacts repositories describe "${REPOSITORY_NAME}" \
    --location="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    log_info "Repository ${REPOSITORY_NAME} already exists"
else
    gcloud artifacts repositories create "${REPOSITORY_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="BARQ Fleet Management Docker images" \
        --project="${PROJECT_ID}"
    log_info "✅ Repository created"
fi

# ================================================================
# STEP 3: Create secrets in Secret Manager
# ================================================================
log_step "3/7 Setting up Secret Manager..."

create_secret() {
    local secret_name=$1
    local default_value=$2

    if gcloud secrets describe "${secret_name}" --project="${PROJECT_ID}" &>/dev/null; then
        log_info "Secret ${secret_name} already exists"
    else
        echo -n "${default_value}" | gcloud secrets create "${secret_name}" \
            --data-file=- \
            --project="${PROJECT_ID}" \
            --replication-policy="automatic"
        log_info "✅ Created secret: ${secret_name}"
    fi
}

# Generate a random secret key if not provided
SECRET_KEY=$(openssl rand -hex 32)

create_secret "barq-secret-key" "${SECRET_KEY}"
create_secret "barq-postgres-password" "CHANGE_THIS_PASSWORD"
create_secret "barq-google-client-id" "YOUR_GOOGLE_CLIENT_ID"
create_secret "barq-google-client-secret" "YOUR_GOOGLE_CLIENT_SECRET"

log_warn "⚠️  Remember to update secrets with actual values:"
echo "    gcloud secrets versions add barq-postgres-password --data-file=- --project=${PROJECT_ID}"
echo "    gcloud secrets versions add barq-google-client-id --data-file=- --project=${PROJECT_ID}"
echo "    gcloud secrets versions add barq-google-client-secret --data-file=- --project=${PROJECT_ID}"

# ================================================================
# STEP 4: Create Cloud Build service account and permissions
# ================================================================
log_step "4/7 Setting up IAM permissions..."

# Get the Cloud Build service account (uses project NUMBER, not ID)
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant necessary roles to Cloud Build service account
ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/artifactregistry.writer"
    "roles/secretmanager.secretAccessor"
    "roles/logging.logWriter"
)

for role in "${ROLES[@]}"; do
    log_info "Granting ${role} to Cloud Build..."
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${CLOUDBUILD_SA}" \
        --role="${role}" \
        --quiet || true
done

log_info "✅ IAM permissions configured"

# ================================================================
# STEP 5: Configure Docker authentication
# ================================================================
log_step "5/7 Configuring Docker authentication..."

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

log_info "✅ Docker authentication configured"

# ================================================================
# STEP 6: Create Cloud Build trigger (optional - manual or GitHub)
# ================================================================
log_step "6/7 Cloud Build trigger setup..."

log_info "To create a Cloud Build trigger, you can either:"
echo ""
echo "  Option A - Connect GitHub repository (recommended):"
echo "    1. Go to: https://console.cloud.google.com/cloud-build/triggers?project=${PROJECT_ID}"
echo "    2. Click 'Create Trigger'"
echo "    3. Connect your GitHub repository"
echo "    4. Configure trigger on push to main branch"
echo "    5. Select 'Cloud Build configuration file' as build type"
echo "    6. Set the path to: cloudbuild.yaml"
echo ""
echo "  Option B - Manual trigger (for testing):"
echo "    gcloud builds submit --config=cloudbuild.yaml --project=${PROJECT_ID}"
echo ""

# ================================================================
# STEP 7: Summary and next steps
# ================================================================
log_step "7/7 Setup complete!"

echo ""
echo "=============================================="
echo "  ✅ GCP Setup Complete!"
echo "=============================================="
echo ""
echo "Resources created:"
echo "  • Artifact Registry: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}"
echo "  • Secrets: barq-secret-key, barq-postgres-password, etc."
echo "  • IAM: Cloud Build permissions configured"
echo ""
echo "Next steps:"
echo ""
echo "  1. UPDATE SECRETS with actual values:"
echo "     echo 'YOUR_DB_PASSWORD' | gcloud secrets versions add barq-postgres-password --data-file=-"
echo ""
echo "  2. SET UP DATABASE (Cloud SQL or external):"
echo "     - Create a PostgreSQL instance"
echo "     - Create the barq_fleet database"
echo "     - Update the database connection secret"
echo ""
echo "  3. DEPLOY manually to test:"
echo "     cd $(pwd)/../.."
echo "     gcloud builds submit --config=cloudbuild.yaml --project=${PROJECT_ID}"
echo ""
echo "  4. SET UP CI/CD trigger (see Step 6 above)"
echo ""
echo "=============================================="
