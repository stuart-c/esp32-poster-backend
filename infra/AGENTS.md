# AGENTS.md (Infrastructure Context)

## Responsibilities
Manage AWS infrastructure using Terraform.

## Terminal Guardrails
- **Allowed:** `terraform init`, `terraform fmt`, `terraform validate`, `terraform plan`, `tflint`.
- **Denied (STRICT):** `terraform apply`, `terraform destroy`.

## Key Architectural Requirements
- **State:** S3 backend using existing S3 bucket.
- **Auth (CRITICAL):** Will use existing OIDC setup for GitHub Actions.
- **Delivery:** Provision a "Processed Storage" S3 bucket with a CloudFront distribution. Use Origin Access Control (OAC) to secure the bucket.
