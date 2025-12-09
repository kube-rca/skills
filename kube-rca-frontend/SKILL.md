---
name: kube-rca-frontend
description: |
  Use when working on frontend code for kube-rca project.
  Triggers: React components, UI development, dashboard,
  alert visualization, frontend/ directory changes.
---

# Kube-RCA Frontend

Frontend application for Kubernetes Root Cause Analysis dashboard.

## Project Structure

```
frontend/
├── README.md
└── LICENSE
```

## Status

Currently in initial state. Future development planned.

## Planned Features

- Alert dashboard with real-time updates
- RCA visualization
- Slack integration status
- Kubernetes cluster overview

## Integration Points

- Backend API: `http://backend:8080`
  - `GET /ping` - Health check
  - `POST /webhook/alertmanager` - Alert webhook (internal)

## Development Guidelines

When implementing:
1. Use TypeScript for type safety
2. Follow React best practices
3. Implement responsive design
4. Consider accessibility (WCAG 2.1 AA)
