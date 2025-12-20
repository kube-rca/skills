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
┌────────────────────────────────────────────────────────────────────────────────────┐
│                                 Kubernetes Cluster                                 │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│ ┌──────────────┐    ┌──────────────┐    ┌────────────────────┐    ┌──────────────┐ │
│ │  Prometheus  │ ─▶ │ Alertmanager │ ─▶ │  kube-rca-backend  │ ─▶ │    Slack     │ │
│ └──────────────┘    └──────────────┘    └─────────┬──────────┘    └──────────────┘ │
│                                                   │ request                        │
│                                                   ▼                                │
│                                           ┌──────────────┐                         │
│                                           │    agent     │                         │
│                                           └───────┬──────┘                         │
│                                                   ▲ result                         │
│                                                   │                                │
│          agent queries: Prometheus (PromQL), Grafana, Cluster Components           │
│ ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                           │
│ │    Alloy     │ ─▶ │     Loki     │ ─▶ │   Grafana    │                           │
│ └──────────────┘    └──────────────┘    └──────────────┘                           │
│                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────┐
│                                       CI/CD                                        │
├────────────────────────────────────────────────────────────────────────────────────┤
│  GitHub Actions ──OIDC──▶ AWS IAM ──▶ ECR ──▶ Argo CD                              │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Repository Structure

```text
kube-rca/
├── backend/          # Go 1.22 + Gin API server (Alertmanager webhook -> Slack)
├── frontend/         # React 18 + TypeScript + Vite + Tailwind CSS
├── helm-charts/      # Helm charts (Argo CD, kube-prometheus-stack, Loki, PostgreSQL, kube-rca)
├── k8s-resources/    # Argo CD Applications, External Secrets
├── terraform/        # Terraform Cloud envs (terraform/envs/dev/)
├── agent/            # Separate agent repository
├── skills/           # Agent skill definitions
└── .github/          # Docs and diagrams
```

## Data Flow

### Alert Flow
1. **Prometheus** scrapes metrics from pods.
2. **Alertmanager** evaluates rules and groups alerts.
3. **Backend API** receives webhook and sends the initial Slack notification.
4. **Backend API** calls `agent/` with the alert payload.
5. **Agent** analyzes the alert by querying Prometheus (PromQL), Grafana, and
   in-cluster components, then returns the RCA result to the backend.
6. **Backend API** sends the analysis result to Slack.

### Log Flow
1. **Alloy** collects container logs.
2. **Loki** stores and indexes logs.
3. **Grafana** provides query interface.

### Deployment Flow
1. **GitHub Actions** builds container image.
2. **AWS ECR** stores image.
3. **Argo CD** syncs to cluster.
4. **Helm** manages releases.

## Cross-Repository Dependencies

| From | To | Dependency |
|------|-----|------------|
| helm-charts | backend | `charts/kube-rca` requires backend image repository/tag values for the Deployment. |
| helm-charts | frontend | `charts/kube-rca` requires frontend image repository/tag values for the Deployment. |
| helm-charts | k8s-resources | Backend Slack Secret defaults to `kube-rca-slack` with keys `kube-rca-slack-token`, `kube-rca-slack-channel-id`. |

## Environment Variables

### Backend
- `SLACK_BOT_TOKEN` - Slack API token
- `SLACK_CHANNEL_ID` - Target channel

## Quick Commands

```bash
# Backend
cd backend && go mod tidy && go run .
cd backend && go test ./...

# Frontend
cd frontend && npm ci
cd frontend && npm run dev
cd frontend && npm run build && npm run lint

# Infra (requires credentials/workspace access)
cd terraform/envs/dev/iam && terraform init && terraform plan
cd helm-charts && helm lint charts/kube-rca
```
