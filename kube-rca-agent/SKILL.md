---
name: kube-rca-agent
description: |
  Python FastAPI-based analysis service for Kube-RCA. Receives Alertmanager payloads,
  performs RCA via Strands Agents and Kubernetes APIs, and returns results.
  Triggers: agent/ directory, app/ layers, pyproject.toml, Dockerfile, FastAPI endpoints.
---

# Kube-RCA Agent

Python FastAPI-based analysis service that receives Alertmanager webhook payloads from the
backend and returns analysis results.

## Project Structure

```
agent/
├── app/
│   ├── api/
│   │   ├── analysis.py
│   │   └── health.py
│   ├── clients/
│   │   ├── k8s.py
│   │   ├── prometheus.py
│   │   ├── strands_agent.py
│   │   └── strands_patch.py
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── logging.py
│   ├── models/
│   │   └── k8s.py
│   ├── schemas/
│   │   ├── alert.py
│   │   └── analysis.py
│   ├── services/
│   │   └── analysis.py
│   └── main.py
├── tests/
│   └── test_analysis_service.py
├── Dockerfile
├── pyproject.toml
└── .github/
    └── workflows/
        └── ci.yaml
```

## Technology Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI + Uvicorn
- **AI Agent**: Strands Agents (Gemini)
- **Kubernetes**: in-cluster service account via Python client
- **CI/CD**: GitHub Actions (Docker, ECR, Helm update)

## Architecture Pattern

**Dependency Flow**: `api → service → clients/models`

## Key Endpoints

- `GET /ping`: Health check (returns pong)
- `GET /healthz`: Liveness probe
- `GET /`: Root info
- `POST /analyze`: Receive and analyze Alertmanager webhooks

## Environment Variables

- `PORT` (default: `8082`)
- `GEMINI_API_KEY` (from Kubernetes Secret)
- `GEMINI_MODEL_ID` (default: `gemini-3-flash-preview`)
- `K8S_API_TIMEOUT_SECONDS` (default: `5`)
- `K8S_EVENT_LIMIT` (default: `20`)
- `K8S_LOG_TAIL_LINES` (default: `50`)
- `PROMETHEUS_LABEL_SELECTOR` (default: `app=kube-prometheus-stack-prometheus`)
- `PROMETHEUS_NAMESPACE_ALLOWLIST` (default: empty = all)
- `PROMETHEUS_PORT_NAME` (default: empty = auto)
- `PROMETHEUS_SCHEME` (default: `http`)
- `PROMETHEUS_HTTP_TIMEOUT_SECONDS` (default: `5`)

## Development Commands

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8082

# Run tests
pytest
```
