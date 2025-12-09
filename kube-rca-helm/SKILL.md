---
name: kube-rca-helm
description: |
  Use when working on Helm charts for kube-rca project.
  Triggers: Kubernetes deployment, Helm values, chart development,
  ArgoCD applications, Prometheus stack, Loki, Alloy,
  helm-charts/ directory, Chart.yaml, values.yaml changes.
---

# Kube-RCA Helm Charts

Helm charts for deploying kube-rca and its dependencies to Kubernetes.

## Project Structure

```
helm-charts/
├── charts/
│   ├── alloy/                    # Grafana Alloy (log collector)
│   ├── argo-applications/        # ArgoCD Application definitions
│   ├── argo-cd/                  # ArgoCD deployment
│   ├── kube-prometheus-stack/    # Prometheus, Alertmanager, Grafana
│   └── loki/                     # Grafana Loki (log aggregation)
└── README.md
```

## Included Charts

### kube-prometheus-stack
- Prometheus for metrics collection
- Alertmanager for alert routing
- Grafana for visualization
- Pre-configured alerting rules

### loki
- Log aggregation
- Query interface
- Integration with Grafana

### alloy
- Log collection agent
- Kubernetes-native deployment
- Push logs to Loki

### argo-cd
- GitOps continuous delivery
- Application sync management

### argo-applications
- ArgoCD Application CRDs
- Defines what to deploy

## Alert Flow

```
Prometheus → Alertmanager → kube-rca-backend → Slack
```

## Key Configurations

### Alertmanager Webhook
```yaml
receivers:
  - name: 'kube-rca'
    webhook_configs:
      - url: 'http://kube-rca-backend:8080/webhook/alertmanager'
```

## Deployment Commands

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

# Install with custom values
helm upgrade --install <release> ./charts/<chart> -f values.yaml
```

## Development Guidelines

1. Use semantic versioning in Chart.yaml
2. Document all values in values.yaml with comments
3. Test with `helm template` before applying
4. Use ArgoCD for GitOps deployments
