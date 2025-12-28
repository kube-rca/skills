---
name: kube-rca-helm
description: |
  Use when working on Helm charts for kube-rca project.
  Triggers: Kubernetes deployment, Helm values, chart development,
  ArgoCD applications, Prometheus stack, Loki, Alloy,
  helm-charts/ directory, Chart.yaml, values.yaml changes.
---

# Kube-RCA Helm Charts

Helm charts for deploying kube-rca and related dependencies to Kubernetes.

## Project Structure

```
helm-charts/
├── charts/
│   ├── alloy/
│   ├── argo-applications/
│   ├── argo-cd/
│   ├── ingress-nginx/
│   ├── kube-prometheus-stack/
│   ├── kube-rca/
│   ├── loki/
│   └── postgresql/
└── README.md
```

## Chart Notes

- `charts/kube-rca/` includes backend/agent/frontend templates, OpenAPI UI(optional), Slack Secret, auth Secret, and agent RBAC + ConfigMap/Secret.
- `charts/kube-prometheus-stack/kube-rca-values.yaml` configures Alertmanager webhook to `POST /webhook/alertmanager`.
- `kube-rca-values.yaml` overrides exist in:
  `charts/argo-applications/`, `charts/argo-cd/`, `charts/alloy/`,
  `charts/ingress-nginx/`, `charts/kube-prometheus-stack/`, `charts/kube-rca/`,
  `charts/loki/`, `charts/postgresql/`.

## Validation Command

```bash
cd helm-charts && helm lint charts/kube-rca
```
