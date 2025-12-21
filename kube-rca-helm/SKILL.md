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
│   ├── kube-prometheus-stack/
│   ├── kube-rca/
│   ├── loki/
│   └── postgresql/
└── README.md
```

## Chart Notes

- `charts/kube-rca/` includes templates for backend, agent, and frontend workloads plus Slack Secret handling.
- `charts/kube-prometheus-stack/kube-rca-values.yaml` configures the Alertmanager receiver for the backend webhook.
- `charts/argo-applications/` and `charts/alloy/` include `kube-rca-values.yaml` overrides.

## Validation Command

```bash
cd helm-charts && helm lint charts/kube-rca
```
