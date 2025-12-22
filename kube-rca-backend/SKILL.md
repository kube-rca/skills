---
name: kube-rca-backend
description: |
  Use when working on Go backend code for kube-rca project.
  Triggers: Alertmanager webhook, Slack client, alert processing,
  Go API development, gin framework, internal/ directory, go.mod changes,
  handler/service/client/model layers, thread management, agent client,
  PostgreSQL database connection.
  Korean triggers: 백엔드, 백엔드 로직, 백엔드 설명, 백엔드 구조, 백엔드 코드,
  Go 코드, 핸들러, 서비스 레이어, 알림 처리, 슬랙 클라이언트, 에이전트 클라이언트.
---

# Kube-RCA Backend

Go-based backend service for Kubernetes Root Cause Analysis.
Receives Alertmanager webhooks, forwards alerts to Slack with thread management,
and integrates with AI Agent for root cause analysis.

## Project Structure

```
backend/
├── main.go                      # Entry point, DI setup, router config
├── internal/
│   ├── handler/
│   │   ├── alert.go             # POST /webhook/alertmanager
│   │   └── health.go            # GET /ping, GET /
│   ├── service/
│   │   ├── alert.go             # Alert filtering, business logic
│   │   └── agent.go             # Agent 분석 요청 및 Slack 응답 처리
│   ├── client/
│   │   ├── slack.go             # Slack API client, thread management
│   │   ├── slack_alert.go       # Alert-specific Slack formatting
│   │   └── agent.go             # Agent HTTP client (POST /analyze)
│   ├── db/
│   │   └── postgres.go          # PostgreSQL connection pool (pgxpool)
│   └── model/
│       └── alert.go             # AlertmanagerWebhook, Alert structs
├── go.mod
└── Dockerfile
```

## Architecture Pattern

**Dependency Flow**: `handler → service → client`

**Initialization Order**: `db → client → service → handler`

## Key Components

### Alertmanager Webhook Handler
- Endpoint: `POST /webhook/alertmanager`
- Parses AlertmanagerWebhook JSON payload
- Delegates to AlertService for processing

### Alert Service
- Filters alerts (shouldSendToSlack)
- Coordinates with SlackClient for delivery
- Triggers AgentService for AI analysis
- Returns sent/failed counts

### Agent Service
- Calls AgentClient.RequestAnalysis (동기 호출)
- Sends analysis result to Slack thread via SlackClient.SendToThread

### Agent Client
- HTTP client for Agent service communication
- Endpoint: `POST /analyze`
- Timeout: 120s (AI 분석 시간 고려)

### Slack Client
- Uses Bot Token (not webhook) for thread_ts support
- Manages fingerprint → thread_ts mapping via sync.Map
- Enables threaded conversations for firing/resolved alerts

### PostgreSQL Connection
- Uses pgxpool for connection pooling
- Supports DATABASE_URL or individual PG* env vars

## Environment Variables

```bash
# Slack
SLACK_BOT_TOKEN=xoxb-...    # Slack Bot Token
SLACK_CHANNEL_ID=C...       # Target channel ID

# Agent
AGENT_URL=http://kube-rca-agent.kube-rca.svc:8000  # Agent service URL

# Database
DATABASE_URL=postgres://user:pass@host:port/dbname?sslmode=disable
# Or individual vars:
PGHOST=localhost
PGPORT=5432
PGUSER=...
PGPASSWORD=...
PGDATABASE=...
PGSSLMODE=disable
```

## Key Patterns

### Thread Management
```go
// Store thread_ts after firing alert
slackClient.StoreThreadTS(fingerprint, response.TS)

// Get thread_ts for resolved alert
threadTS, ok := slackClient.GetThreadTS(fingerprint)

// Cleanup after resolved
slackClient.DeleteThreadTS(fingerprint)
```

### Agent Analysis Flow
```go
// AgentService.RequestAnalysis (동기 호출)
resp, err := s.agentClient.RequestAnalysis(alert, threadTS)
s.slackClient.SendToThread(threadTS, resp.Analysis)
```

### Alert Status Colors
- critical: `#dc3545` (red)
- warning: `#ffc107` (yellow)
- resolved: `#36a64f` (green)

## Dependencies

- `gin-gonic/gin` - HTTP router
- `jackc/pgx/v5` - PostgreSQL driver
- Go 1.22+

## Future Plans

- K8s client for cluster state inspection
