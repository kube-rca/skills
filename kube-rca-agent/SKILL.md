---
name: kube-rca-agent
description: |
  Python FastAPI-based analysis service for Kube-RCA. Receives Alertmanager payloads
  from the backend, gathers Kubernetes/Prometheus context, runs Strands Agents (Gemini),
  and returns RCA summaries. Triggers: agent/ directory, app/ layers, pyproject.toml,
  Dockerfile, FastAPI endpoints, Makefile.
---

# Kube-RCA Agent

Python FastAPI 기반 분석 서비스로, Backend에서 전달받은 Alertmanager webhook payload를
Kubernetes/Prometheus 컨텍스트와 Strands Agents(Gemini)를 활용해 분석하고 결과를 반환합니다.

## Project Structure

```text
agent/
├── app/
│   ├── api/
│   │   ├── analysis.py          # POST /analyze
│   │   └── health.py            # GET /ping, /healthz, /
│   ├── clients/
│   │   ├── k8s.py               # Kubernetes API client
│   │   ├── prometheus.py        # Prometheus instant query client
│   │   ├── strands_agent.py     # Strands Agent wrapper (13 tools)
│   │   └── strands_patch.py     # Gemini thought signature patch
│   ├── core/
│   │   ├── config.py            # Settings dataclass (env vars)
│   │   ├── dependencies.py      # FastAPI DI (lru_cache singletons)
│   │   └── logging.py           # Logging configuration
│   ├── models/
│   │   └── k8s.py               # Domain models (K8sContext, PodStatusSnapshot, ...)
│   ├── schemas/
│   │   ├── alert.py             # Alert Pydantic schema
│   │   └── analysis.py          # Request/Response schemas
│   ├── services/
│   │   └── analysis.py          # Analysis orchestration service
│   └── main.py                  # FastAPI app entrypoint
├── docs/
│   ├── openapi.json             # Generated OpenAPI document
│   └── session-context-analysis.md # Session context notes
├── scripts/
│   └── export_openapi.py        # OpenAPI export helper
├── tests/
│   └── test_analysis_service.py # Unit tests with fake clients
├── Dockerfile                   # Python 3.12-slim + uv
├── Makefile                     # Dev/test automation
├── pyproject.toml               # Dependencies (hatchling build)
└── uv.lock
```

## Technology Stack

| Category | Technology | Version |
|----------|------------|---------|
| Language | Python | >=3.10 |
| Framework | FastAPI + Uvicorn | >=0.115.12 / >=0.34.2 |
| AI Agent | Strands Agents (Gemini) | >=1.20.0 |
| Session Store | PostgreSQL (psycopg[binary]) | >=3.2.0 |
| Kubernetes | kubernetes-client | >=34.0.0 |
| Validation | Pydantic | >=2.4.0 |
| Build | Hatchling | - |
| Lint/Format | Ruff | >=0.13.0 |
| Package Manager | uv | - |

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
│  ├── k8s.py: KubernetesClient                                   │
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

## Key Behavior

- `GEMINI_API_KEY`가 없으면 Strands 분석 엔진을 비활성화하고 fallback 요약을 반환합니다.
- `GEMINI_API_KEY`를 설정한 경우 `SESSION_DB_HOST`, `SESSION_DB_USER`, `SESSION_DB_NAME`가 필요하며,
  누락 시 AnalysisEngine 초기화 에러가 발생합니다.

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ping` | Health check (returns `{"message": "pong"}`) |
| GET | `/healthz` | Liveness probe (returns `{"status": "ok"}`) |
| GET | `/` | Root info |
| POST | `/analyze` | Receive Alertmanager payload, perform RCA, return analysis |

### POST /analyze Request/Response

**Request (incident_id optional):**

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
  "thread_ts": "1234567890.123456",
  "incident_id": "incident-abc123"
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
| `GEMINI_API_KEY` | (optional) | Gemini API key (없으면 fallback 요약) |
| `GEMINI_MODEL_ID` | `gemini-3-flash-preview` | Gemini model ID |
| `SESSION_DB_HOST` | (empty) | Postgres session store host |
| `SESSION_DB_PORT` | `5432` | Postgres session store port |
| `SESSION_DB_NAME` | (empty) | Postgres session store database name |
| `SESSION_DB_USER` | (empty) | Postgres session store user |
| `SESSION_DB_PASSWORD` | (empty) | Postgres session store password (if required) |
| `AGENT_CACHE_SIZE` | `128` | Cached agent entries (LRU) |
| `AGENT_CACHE_TTL_SECONDS` | `0` | Cache TTL seconds (0 = disable TTL) |
| `K8S_API_TIMEOUT_SECONDS` | `5` | Kubernetes API timeout |
| `K8S_EVENT_LIMIT` | `20` | Max events to fetch |
| `K8S_LOG_TAIL_LINES` | `50` | Log tail lines |
| `PROMETHEUS_LABEL_SELECTOR` | `app=kube-prometheus-stack-prometheus` | Prometheus service selector |
| `PROMETHEUS_NAMESPACE_ALLOWLIST` | (empty = all) | Allowed namespaces for Prometheus |
| `PROMETHEUS_PORT_NAME` | (empty = auto) | Prometheus service port name |
| `PROMETHEUS_SCHEME` | `http` | Prometheus scheme |
| `PROMETHEUS_HTTP_TIMEOUT_SECONDS` | `5` | Prometheus HTTP timeout |

## Kubernetes RBAC Requirements

Agent는 `get`, `list`, `watch` 권한이 필요합니다.
Helm chart의 ClusterRole은 `apiGroups: ["*"], resources: ["*"]`로 설정되어 있습니다.

## Development Commands

```bash
# Install dependencies
cd agent
make install

# Setup pre-commit hooks (run once after clone)
pre-commit install

# Run locally
make run  # PORT=8000

# Lint
make lint

# Format
make format

# Run tests
make test

# Run pre-commit checks manually
pre-commit run --all-files

# Build Docker image
make build IMAGE=<your-image>
```

## Pre-commit Hooks

`.pre-commit-config.yaml`에 정의된 hook들:

| Hook | Description |
|------|-------------|
| `ruff-format` | Python 코드 포맷 검사 |
| `ruff-check` | Python 린트 검사 |
| `export-openapi` | OpenAPI spec 자동 생성 및 변경 감지 |

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
- `clusterrole.yaml`: ClusterRole (get/list/watch)
- `clusterrolebinding.yaml`: ClusterRoleBinding
- `configmap.yaml`: Agent configuration
- `secret.yaml`: Gemini API key Secret
- `ingress.yaml`: Optional Ingress

## Verification Before Git Commit/Push

1. `make lint` 통과 확인
2. `make test` 통과 확인
3. 변경사항 커밋 및 푸시
