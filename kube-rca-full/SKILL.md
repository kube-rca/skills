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
│                                      ┌─────────────────────┐                       │
│                                      │      frontend       │                       │
│                                      │    (RCA list UI)    │                       │
│                                      └─────────┬───────────┘                       │
│                                                │ request                           │
│                                                ▼                                   │
│ ┌──────────────┐    ┌──────────────┐    ┌────────────────────┐    ┌──────────────┐ │
│ │  Prometheus  │ ─▶ │ Alertmanager │ ─▶ │      backend       │ ─▶ │    Slack     │ │
│ └──────────────┘    └──────────────┘    └─────────┬──────────┘    └──────────────┘ │
│                                                   │ request                        │
│                                                   ▼                                │
│                                           ┌──────────────┐                         │
│                                           │     agent    │                         │
│                                           └───────┬──────┘                         │
│                                                   │                                │
│                         queries: K8s API, Prometheus (PromQL)                      │
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
├── agent/            # Python FastAPI analysis service
├── skills/           # Agent skill definitions
└── .github/          # Docs and diagrams
```

## Data Flow

### Alert Flow
1. **Prometheus** scrapes metrics from pods.
2. **Alertmanager** evaluates rules and groups alerts.
3. **Backend API** receives webhook and sends the initial Slack notification.
4. **Backend API** calls `agent/` with the alert payload.
5. **Agent** analyzes the alert via K8s API and Prometheus (PromQL), then
   returns the RCA result to the backend.
6. **Backend API** sends the analysis result to Slack.

### Frontend Flow
1. **Frontend** requests RCA list from backend (`/api/rca` in client code).
2. **Backend** should provide RCA list endpoints (currently `/api/v1/incidents`).

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
| helm-charts | agent | `charts/kube-rca` requires agent image repository/tag values for the Deployment. |
| helm-charts | k8s-resources | Backend Slack Secret defaults to `kube-rca-slack` with keys `kube-rca-slack-token`, `kube-rca-slack-channel-id`. |

## Environment Variables

### Backend
- `SLACK_BOT_TOKEN` - Slack API token
- `SLACK_CHANNEL_ID` - Target channel
- `AGENT_URL` - Agent base URL (default: `http://kube-rca-agent.kube-rca.svc:8000`)
- `DATABASE_URL` or `PG*` - PostgreSQL connection

### Agent
- `PORT` - Service port (default: 8000)
- `GEMINI_API_KEY` - Gemini API key (required)
- `GEMINI_MODEL_ID` - Gemini model ID (default: `gemini-3-flash-preview`)

## Quick Commands

```bash
# Backend
cd backend && go mod tidy && go run .
cd backend && go test ./...

# Frontend
cd frontend && npm ci
cd frontend && npm run dev
cd frontend && npm run build && npm run lint

# Agent
cd agent && make install
cd agent && make run

# Infra (requires credentials/workspace access)
cd terraform/envs/dev/iam && terraform init && terraform plan
cd helm-charts && helm lint charts/kube-rca
```
