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
│  ┌─────────────────────┐        ┌────────────────────┐        ┌──────────────┐     │
│  │      frontend       │ ─────▶ │      backend       │ ─────▶ │    Slack     │     │
│  │  (auth + RCA UI)    │        │  (auth/rca/alert)  │        └──────────────┘     │
│  └─────────┬───────────┘        └─────────┬──────────┘                             │
│            │                              │                                        │
│            ▼                              ▼                                        │
│     ┌──────────────┐                ┌──────────────┐                               │
│     │ PostgreSQL   │                │     agent    │                               │
│     │ incidents    │                │  (FastAPI)   │                               │
│     │ auth/embeds  │                └───────┬──────┘                               │
│     └──────────────┘                        │                                      │
│                                             │ queries: K8s API, Prometheus         │
│                                             ▼                                      │
│                                      ┌──────────────┐                              │
│                                      │   Gemini     │                              │
│                                      │ (LLM/Embed)  │                              │
│                                      └──────────────┘                              │
│                                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                          │
│  │  Prometheus  │ ─▶ │ Alertmanager │ ── webhook ──▶ │   backend    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘                          │
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
├── backend/          # Go 1.24 + Gin API server (Alertmanager webhook -> Slack)
├── frontend/         # React 18 + TypeScript + Vite + Tailwind CSS
├── helm-charts/      # Helm charts (Argo CD, kube-prometheus-stack, Loki, PostgreSQL, ingress-nginx, kube-rca)
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
5. **Agent** analyzes the alert via K8s API and Prometheus, then returns results.
6. **Backend API** sends the analysis result to the Slack thread.

### Auth Flow
1. **Frontend** calls `/api/v1/auth/config` and `/api/v1/auth/refresh` to initialize auth.
2. **Login/Register** via `/api/v1/auth/login|register` returns access token and sets refresh cookie.
3. **Protected APIs** use `Authorization: Bearer <token>` and refresh cookie on 401.
4. **Logout** revokes refresh token and clears cookie (`/api/v1/auth/logout`).

### Frontend Flow
1. **Frontend** requests RCA list from backend (`GET /api/v1/incidents`).
2. **Frontend** requests incident detail (`GET /api/v1/incidents/:id`) and updates (`PUT /api/v1/incidents/:id`).

### Embedding Flow
1. **Backend** receives `POST /api/v1/embeddings`.
2. **Backend** calls Gemini embedding API and stores vectors in PostgreSQL (pgvector).

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
| helm-charts | k8s-resources | Backend auth Secret keys: `admin-username`, `admin-password`, `kube-rca-jwt-secret`. |

## Environment Variables

### Backend
- `SLACK_BOT_TOKEN` - Slack API token
- `SLACK_CHANNEL_ID` - Target channel
- `AGENT_URL` - Agent base URL (default: `http://kube-rca-agent.kube-rca.svc:8000`)
- `AI_API_KEY` - Gemini API key for embeddings (required)
- `DATABASE_URL` or `PG*` - PostgreSQL connection
- `JWT_SECRET` - JWT signing secret (required)
- `JWT_ACCESS_TTL`, `JWT_REFRESH_TTL`
- `ALLOW_SIGNUP`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- `AUTH_COOKIE_SECURE`, `AUTH_COOKIE_SAMESITE`, `AUTH_COOKIE_DOMAIN`, `AUTH_COOKIE_PATH`
- `CORS_ALLOWED_ORIGINS`

### Agent
- `PORT` - Service port (default: 8000)
- `GEMINI_API_KEY` - Gemini API key (optional, 없으면 fallback)
- `GEMINI_MODEL_ID` - Gemini model ID (default: `gemini-3-flash-preview`)
- `K8S_API_TIMEOUT_SECONDS`, `K8S_EVENT_LIMIT`, `K8S_LOG_TAIL_LINES`
- `PROMETHEUS_LABEL_SELECTOR`, `PROMETHEUS_NAMESPACE_ALLOWLIST`, `PROMETHEUS_PORT_NAME`
- `PROMETHEUS_SCHEME`, `PROMETHEUS_HTTP_TIMEOUT_SECONDS`

### Frontend
- `VITE_API_BASE_URL` - Backend base URL (없으면 동일 오리진)

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
