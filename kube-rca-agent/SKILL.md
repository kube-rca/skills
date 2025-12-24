---
name: kube-rca-agent
description: |
  Python FastAPI-based analysis service for Kube-RCA. Receives Alertmanager payloads,
  performs RCA via Strands Agents (Gemini) and Kubernetes APIs, and returns results.
  Triggers: agent/ directory, app/ layers, pyproject.toml, Dockerfile, FastAPI endpoints.
---

# Kube-RCA Agent

Python FastAPI 기반 분석 서비스로, Backend에서 전달받은 Alertmanager webhook payload를
Strands Agents(Gemini LLM)와 Kubernetes API를 활용해 분석하고 결과를 반환합니다.

## Project Structure

```text
agent/
├── app/
│   ├── api/
│   │   ├── analysis.py          # POST /analyze endpoint
│   │   └── health.py            # GET /ping, /healthz, / endpoints
│   ├── clients/
│   │   ├── k8s.py               # Kubernetes API client (CoreV1, AppsV1, BatchV1, CustomObjects)
│   │   ├── prometheus.py        # Prometheus instant query client
│   │   ├── strands_agent.py     # Strands Agent wrapper with 13 tools
│   │   └── strands_patch.py     # Gemini thought signature patch
│   ├── core/
│   │   ├── config.py            # Settings dataclass (env vars)
│   │   ├── dependencies.py      # FastAPI DI (lru_cache singletons)
│   │   └── logging.py           # Logging configuration
│   ├── models/
│   │   └── k8s.py               # Domain models (PodStatusSnapshot, K8sContext, etc.)
│   ├── schemas/
│   │   ├── alert.py             # Alert Pydantic schema
│   │   └── analysis.py          # Request/Response schemas
│   ├── services/
│   │   └── analysis.py          # Analysis orchestration service
│   └── main.py                  # FastAPI app entrypoint
├── tests/
│   └── test_analysis_service.py # Unit tests with fake clients
├── scripts/
│   ├── curl-test-oomkilled.sh   # OOMKilled test automation
│   ├── curl-test-crashloop.sh   # CrashLoopBackOff test automation
│   └── curl-test-imagepull.sh   # ImagePullBackOff test automation
├── Dockerfile                   # Python 3.12-slim + uv
├── Makefile                     # Development/test automation
├── pyproject.toml               # Dependencies (hatchling build)
└── README.md
```

## Technology Stack

| Category | Technology | Version |
|----------|------------|---------|
| Language | Python | 3.10+ |
| Framework | FastAPI + Uvicorn | 0.115+ |
| AI Agent | Strands Agents (Gemini) | 1.20+ |
| Kubernetes | kubernetes-client | 34.x |
| Validation | Pydantic | 2.4+ |
| Build | Hatchling | - |
| Linting | Ruff | 0.13+ |
| Package Manager | uv | - |
| CI/CD | GitHub Actions | - |

## Architecture Pattern

```text
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI App                             │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (api/)                                               │
│  ├── health.py: /ping, /healthz, /                              │
│  └── analysis.py: POST /analyze                                 │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer (services/)                                      │
│  └── analysis.py: AnalysisService (orchestration)               │
├─────────────────────────────────────────────────────────────────┤
│  Client Layer (clients/)                                        │
│  ├── k8s.py: KubernetesClient (sync, CoreV1/AppsV1/BatchV1)     │
│  ├── prometheus.py: PrometheusClient (instant query)            │
│  └── strands_agent.py: StrandsAnalysisEngine (13 tools)         │
├─────────────────────────────────────────────────────────────────┤
│  Core Layer (core/)                                             │
│  ├── config.py: Settings (dataclass, env vars)                  │
│  ├── dependencies.py: DI (lru_cache singletons)                 │
│  └── logging.py: Logging setup                                  │
├─────────────────────────────────────────────────────────────────┤
│  Domain Models (models/, schemas/)                              │
│  ├── models/k8s.py: K8sContext, PodStatusSnapshot, etc.         │
│  └── schemas/: Alert, AlertAnalysisRequest/Response             │
└─────────────────────────────────────────────────────────────────┘
```

**Dependency Flow**: `api → service → clients/models → core`

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ping` | Health check (returns `{"message": "pong"}`) |
| GET | `/healthz` | Liveness probe (returns `{"status": "ok"}`) |
| GET | `/` | Root info |
| POST | `/analyze` | Receive Alertmanager payload, perform RCA, return analysis |

### POST /analyze Request/Response

**Request:**

```json
{
  "alert": {
    "status": "firing",
    "labels": {"alertname": "OOMKilled", "namespace": "default", "pod": "demo-pod"},
    "annotations": {"summary": "Pod OOMKilled"},
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "0001-01-01T00:00:00Z",
    "generatorURL": "",
    "fingerprint": "abc123"
  },
  "thread_ts": "1234567890.123456"
}
```

**Response:**

```json
{
  "status": "ok",
  "thread_ts": "1234567890.123456",
  "analysis": "## 근본 원인 분석\n..."
}
```

## Strands Agent Tools (13 Tools)

| Tool | Description |
|------|-------------|
| `get_pod_status` | Pod 상태(phase, conditions, container statuses) 조회 |
| `get_pod_spec` | Pod 스펙 요약(containers, resources, probes) 조회 |
| `list_pod_events` | Pod 관련 이벤트 목록 조회 |
| `list_namespace_events` | Namespace 전체 이벤트 목록 조회 |
| `list_cluster_events` | 클러스터 전체 이벤트 목록 조회 |
| `get_previous_pod_logs` | 이전(재시작 전) 컨테이너 로그 조회 |
| `get_pod_logs` | 현재 컨테이너 로그 조회 |
| `get_workload_status` | 상위 워크로드(Deployment/StatefulSet/Job 등) 상태 조회 |
| `get_node_status` | 노드 상태(conditions, capacity, taints) 조회 |
| `get_pod_metrics` | Pod CPU/Memory 사용량 (metrics-server) 조회 |
| `get_node_metrics` | Node CPU/Memory 사용량 (metrics-server) 조회 |
| `discover_prometheus` | 클러스터 내 Prometheus 서비스 엔드포인트 탐색 |
| `query_prometheus` | Prometheus instant query 실행 |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `info` | Logging level |
| `GEMINI_API_KEY` | (required) | Gemini API key (from Secret) |
| `GEMINI_MODEL_ID` | `gemini-3-flash-preview` | Gemini model ID |
| `K8S_API_TIMEOUT_SECONDS` | `5` | Kubernetes API timeout |
| `K8S_EVENT_LIMIT` | `20` | Max events to fetch |
| `K8S_LOG_TAIL_LINES` | `50` | Log tail lines |
| `PROMETHEUS_LABEL_SELECTOR` | `app=kube-prometheus-stack-prometheus` | Prometheus service selector |
| `PROMETHEUS_NAMESPACE_ALLOWLIST` | (empty = all) | Allowed namespaces for Prometheus |
| `PROMETHEUS_PORT_NAME` | (empty = auto) | Prometheus service port name |
| `PROMETHEUS_SCHEME` | `http` | Prometheus scheme |
| `PROMETHEUS_HTTP_TIMEOUT_SECONDS` | `5` | Prometheus HTTP timeout |

## Kubernetes RBAC Requirements

Agent는 다음 리소스에 대한 `get`, `list`, `watch` 권한이 필요합니다:

- `pods`, `pods/log` (CoreV1)
- `events` (CoreV1)
- `nodes` (CoreV1)
- `services` (CoreV1)
- `deployments`, `replicasets`, `statefulsets`, `daemonsets` (AppsV1)
- `jobs`, `cronjobs` (BatchV1)
- `pods` (metrics.k8s.io - CustomObjects)
- `nodes` (metrics.k8s.io - CustomObjects)

Helm chart에서는 `apiGroups: ["*"], resources: ["*"]`로 설정되어 있습니다.

## Development Commands

```bash
# Install dependencies
cd agent
make install

# Run locally
make run  # PORT=8000

# Run with custom port
PORT=8082 make run

# Lint
make lint

# Format
make format

# Run tests
make test

# Build Docker image
make build IMAGE=<your-image>
```

## Testing Commands

```bash
# Create OOMKilled test pod
make test-oom-only

# Create CrashLoopBackOff test pod
make test-crash-only

# Create ImagePullBackOff test pod
make test-imagepull-only

# Call analyze endpoint via curlpod (in-cluster)
make curl-analyze

# Call analyze endpoint on localhost
make curl-analyze-local ALERT_NAMESPACE=default ALERT_POD=demo-pod

# Full local test (requires GEMINI_API_KEY, KUBECONFIG)
GEMINI_API_KEY=<key> KUBECONFIG=<path> make test-analysis-local

# Cleanup test deployments
make cleanup-oom
make cleanup-crash
make cleanup-imagepull
```

## Helm Chart Integration

Agent는 `helm-charts/charts/kube-rca/templates/agent/` 아래에 배포됩니다:

- `deployment.yaml`: Agent Deployment
- `service.yaml`: ClusterIP Service
- `serviceaccount.yaml`: ServiceAccount
- `clusterrole.yaml`: ClusterRole (read-only cluster-wide)
- `clusterrolebinding.yaml`: ClusterRoleBinding
- `configmap.yaml`: Agent configuration
- `secret.yaml`: Gemini API key Secret
- `ingress.yaml`: Optional Ingress

## Verification Before Git Commit/Push

1. `make lint` 통과 확인
2. `make test` 통과 확인
3. 변경사항 커밋 및 푸시
