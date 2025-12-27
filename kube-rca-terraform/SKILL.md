---
name: kube-rca-terraform
description: |
  Use when working on infrastructure code for kube-rca project.
  Triggers: Terraform, AWS resources, ECR, IAM, GitHub Actions OIDC,
  infrastructure provisioning, terraform/ directory, .tf file changes.
---

# Kube-RCA Terraform

Infrastructure as Code for kube-rca AWS resources.

## Project Structure

```
terraform/
├── envs/
│   └── dev/
│       ├── ecr-public/
│       │   ├── ecr.tf           # ECR Public repository
│       │   ├── variables.tf
│       │   ├── outputs.tf
│       │   └── versions.tf
│       └── iam/
│           ├── iam.tf           # IAM roles and policies
│           ├── github_oidc.tf   # GitHub Actions OIDC provider
│           ├── variables.tf
│           ├── outputs.tf
│           ├── versions.tf
│           └── template/
│               ├── force_mfa_policy.json
│               ├── github_actions_oidc_trust.json
│               └── github_actions_ecr_push.json
├── .gitignore
├── .terraform-version
└── README.md
```

## Resources

### ECR Public
- Repository: `kube-rca-ecr`
- Region: us-east-1 (required for ECR Public)
- Used for: Container image storage

### GitHub Actions OIDC
- Enables keyless authentication from GitHub Actions
- Organization: `kube-rca`
- Role: `kube-rca-github-actions-oidc-role`

### IAM Policies
- ECR push permissions for GitHub Actions
- IAM user group + MFA 강제 정책 (Force-MFA)
- Scoped to account ECR repositories

## Key Configurations

### OIDC Provider
```hcl
locals {
  github_org                 = "kube-rca"
  github_oidc_role_name      = "kube-rca-github-actions-oidc-role"
  github_oidc_provider_url   = "https://token.actions.githubusercontent.com"
  github_oidc_audience       = "sts.amazonaws.com"
  github_oidc_thumbprint_sha = "6938fd4d98bab03faadb97b34396831e3780aea1"
}
```

## Workflow

```
GitHub Actions → OIDC → AWS IAM → ECR Push
```

## Commands

```bash
# IAM workspace (Terraform Cloud)
cd terraform/envs/dev/iam && terraform init && terraform plan

# ECR Public workspace (Terraform Cloud)
cd terraform/envs/dev/ecr-public && terraform init && terraform plan
```

## Development Guidelines

1. Terraform Cloud workspaces: `iam`, `ecr`
2. Keep IAM least-privilege policies
3. Use templatefile() for JSON policies
4. Pin provider versions in versions.tf
