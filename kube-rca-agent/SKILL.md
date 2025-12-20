---
name: kube-rca-agent
description: |
  Use when working on the kube-rca agent service.
  Triggers: agent/ directory, Go Gin server for analysis, Alertmanager payload analysis,
  agent API endpoints, internal/ handler/service/model layers, go.mod changes in agent repo.
---

# Kube-RCA Agent

Go-based analysis service that receives Alertmanager webhook payloads from the backend
and returns basic analysis results.

## Project Structure

```
agent/
├── main.go
├── internal/
│   ├── handler/
│   │   ├── analysis.go
│   │   └── health.go
│   ├── service/
│   │   └── analysis.go
│   └── model/
│       ├── alert.go
│       └── analysis.go
├── go.mod
└── Dockerfile
```

## Architecture Pattern

**Dependency Flow**: `handler → service → model`

## Key Endpoints

- `POST /analyze/alertmanager`
- `GET /ping`
- `GET /healthz`
- `GET /`

## Environment Variables

- `PORT` (default 8082)
