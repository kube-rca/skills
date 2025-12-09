---
name: kube-rca-full
description: |
  Use for cross-repository tasks spanning multiple kube-rca components.
  Triggers: Full system design, end-to-end flow, integration between
  backend/frontend/helm/terraform, architecture decisions, deployment pipeline,
  multi-repo changes, system-wide refactoring.
---

# Kube-RCA Full Project

Kubernetes Root Cause Analysis - Complete System Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Prometheus  │───▶│ Alertmanager │───▶│ kube-rca-backend │  │
│  └──────────────┘    └──────────────┘    └────────┬─────────┘  │
│         │                                          │             │
│         │            ┌──────────────┐              │             │
│         └───────────▶│   Grafana    │              │             │
│                      └──────────────┘              │             │
│                                                    ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │    Alloy     │───▶│     Loki     │    │      Slack       │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           CI/CD                                  │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Actions ──OIDC──▶ AWS IAM ──▶ ECR ──▶ ArgoCD            │
└─────────────────────────────────────────────────────────────────┘
```

## Repository Structure

```
kube-rca/
├── backend/          # Go API server (Alertmanager → Slack)
├── frontend/         # Dashboard UI (planned)
├── helm-charts/      # Kubernetes deployments
└── terraform/        # AWS infrastructure
```

## Data Flow

### Alert Flow
1. **Prometheus** scrapes metrics from pods
2. **Alertmanager** evaluates rules, groups alerts
3. **kube-rca-backend** receives webhook, formats message
4. **Slack** displays alert with thread support

### Log Flow
1. **Alloy** collects container logs
2. **Loki** stores and indexes logs
3. **Grafana** provides query interface

### Deployment Flow
1. **GitHub Actions** builds container image
2. **AWS ECR** stores image
3. **ArgoCD** syncs to cluster
4. **Helm** manages releases

## Cross-Repository Dependencies

| From | To | Dependency |
|------|-----|------------|
| helm-charts | backend | Container image from ECR |
| helm-charts | terraform | ECR repository URL |
| backend | helm-charts | Alertmanager webhook config |
| terraform | backend | GitHub Actions workflow |

## Environment Variables

### Backend
- `SLACK_BOT_TOKEN` - Slack API token
- `SLACK_CHANNEL_ID` - Target channel

### Terraform
- `AWS_REGION` - AWS region
- `TF_STATE_BUCKET` - State storage (if configured)

## Future Roadmap

1. **AI RCA Integration** - Analyze alerts with LLM
2. **K8s Client** - Inspect cluster state on alert
3. **Frontend Dashboard** - Visualize alerts and RCA
4. **Multi-cluster** - Support multiple K8s clusters

## Quick Commands

```bash
# Backend development
cd backend && go run main.go

# Helm deployment
cd helm-charts && helm upgrade --install kube-rca ./charts/...

# Terraform apply
cd terraform/envs/dev/ecr-public && terraform apply
```
