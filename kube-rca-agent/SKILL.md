---
name: kube-rca-agent
description: |
  Go-based analysis service for Kube-RCA. Receives Alertmanager payloads,
  performs RCA (Root Cause Analysis), and returns results.
  Triggers: agent/ directory, internal/ handler/service/model layers, go.mod, main.go.
---

# Kube-RCA Agent

Go-based analysis service that receives Alertmanager webhook payloads from the backend
and returns basic analysis results.

## Project Structure

```
agent/
├── main.go
├── go.mod
├── go.sum
├── Dockerfile
├── internal/
│   ├── handler/
│   │   ├── analysis.go
│   │   └── health.go
│   ├── service/
│   │   ├── analysis.go
│   │   └── analysis_test.go
│   └── model/
│       ├── alert.go
│       └── analysis.go
└── .github/
    └── workflows/
        └── ci.yaml
```

## Technology Stack

- **Language**: Go 1.22+
- **Framework**: Gin Web Framework
- **CI/CD**: GitHub Actions (Docker, ECR, Helm update)

## Architecture Pattern

**Dependency Flow**: `handler → service → model`

## Key Endpoints

- `GET /ping`: Health check (returns pong)
- `GET /healthz`: Liveness probe
- `GET /`: Root info
- `POST /analyze/alertmanager`: Receive and analyze Alertmanager webhooks

## Environment Variables

- `PORT` (default: `8082`)

## Development Commands

```bash
# Initialize/Tidy dependencies
go mod tidy

# Run locally
go run .

# Run tests
go test ./...
```