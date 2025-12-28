---
name: kube-rca-backend
description: |
  Use when working on Go backend code for kube-rca project.
  Triggers: Alertmanager webhook, Slack client, auth flow, incident/embedding APIs,
  Go API development, gin framework, internal/ directory, go.mod changes,
  handler/service/client/model layers, thread management, agent client,
  PostgreSQL database connection.
  Korean triggers: 백엔드, 백엔드 로직, 백엔드 설명, 백엔드 구조, 백엔드 코드,
  Go 코드, 핸들러, 서비스 레이어, 알림 처리, 슬랙 클라이언트, 에이전트 클라이언트, 인증.
---

# Kube-RCA Backend

Go 기반 Backend 서비스로 Alertmanager 웹훅 수신, Slack 알림 전송,
Agent 분석 요청, 인증(JWT+Refresh), Incident/Embedding API를 제공합니다.

## Project Structure

```
backend/
├── main.go                      # Entry point, DI setup, router config
├── internal/
│   ├── config/
│   │   └── config.go            # Env config loader
│   ├── handler/
│   │   ├── alert.go             # POST /webhook/alertmanager
│   │   ├── auth.go              # /api/v1/auth/*
│   │   ├── embedding.go         # POST /api/v1/embeddings
│   │   ├── health.go            # GET /ping, GET /
│   │   ├── middleware.go        # Auth/CORS middleware
│   │   ├── openapi.go           # GET /openapi.json
│   │   └── rca.go               # /api/v1/incidents*
│   ├── service/
│   │   ├── alert.go             # Alert filtering, Slack 전송
│   │   ├── agent.go             # Agent 분석 요청 및 Slack 응답 처리
│   │   ├── auth.go              # JWT/refresh token auth
│   │   ├── embedding.go         # Embedding orchestration
│   │   └── rca.go               # Incident 조회/수정
│   ├── client/
│   │   ├── agent.go             # Agent HTTP client (POST /analyze)
│   │   ├── genai.go             # Gemini embedding client
│   │   ├── slack.go             # Slack API client, thread management
│   │   └── slack_alert.go       # Alert-specific Slack formatting
│   ├── db/
│   │   ├── auth.go              # users/refresh_tokens schema + queries
│   │   ├── embedding.go         # embeddings insert
│   │   ├── postgres.go          # PostgreSQL connection pool
│   │   └── rca.go               # Incident queries
│   └── model/
│       ├── alert.go             # AlertmanagerWebhook, Alert structs
│       ├── auth.go              # Auth DTOs
│       ├── embedding.go         # Embedding DTOs
│       └── rca.go               # Incident DTOs
├── docs/                        # Generated OpenAPI (swagger)
├── go.mod
└── Dockerfile
```

## Architecture Pattern

**Dependency Flow**: `handler → service → client/db`

**Initialization Order**:
- `db pool → auth/rca/embedding service → handlers`
- `client → service → handler`

## Key Components

### Alertmanager Webhook Handler
- Endpoint: `POST /webhook/alertmanager`
- Parses AlertmanagerWebhook JSON payload
- Delegates to AlertService for processing

### Alert Service
- Filters alerts (`shouldSendToSlack`)
- Coordinates with SlackClient for delivery
- Triggers AgentService asynchronously (goroutine per alert)
- Returns sent/failed counts

### Agent Service
- AlertService에서 goroutine으로 호출 (알림 단위 비동기 처리)
- AgentClient가 `POST /analyze` 동기 호출 (timeout 120s)
- 분석 결과를 Slack 스레드에 전송

### Slack Client
- Bot token 기반 `chat.postMessage` 사용 (thread_ts 필요)
- fingerprint → thread_ts 매핑을 `sync.Map`에 보관/삭제
- firing/resolved/분석 결과를 동일 스레드에 전송

### PostgreSQL Connection
- `pgxpool` 기반 연결, `DATABASE_URL` 또는 `PG*` 조합 사용
- `NewPostgresPool`에서 Ping 성공 시 서비스 시작
- `DATABASE_URL` 미설정 시 `PGUSER/PGDATABASE` 누락이면 오류

### Auth Service
- 엔드포인트:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/config`
  - `GET /api/v1/auth/me`
- JWT Access Token + Refresh Token Cookie(`kube_rca_refresh`)
- 시작 시 users/refresh_tokens 스키마 생성 및 admin 계정 보장

### RCA API Handler
- `GET /api/v1/incidents`
- `GET /api/v1/incidents/:id`
- `PUT /api/v1/incidents/:id`
- `POST /api/v1/incidents/mock`

### Embedding API Handler
- `POST /api/v1/embeddings`
- Gemini Embedding(`text-embedding-004`)으로 벡터 생성 후 pgvector에 저장

### OpenAPI
- `GET /openapi.json` (backend/docs 기반)

## Environment Variables

```bash
# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C...

# Agent
AGENT_URL=http://kube-rca-agent.kube-rca.svc:8000

# Embedding (Gemini)
AI_API_KEY=...  # Gemini API key (필수)

# Database
DATABASE_URL=postgres://user:pass@host:port/dbname?sslmode=disable
# Or individual vars:
PGHOST=localhost
PGPORT=5432
PGUSER=...
PGPASSWORD=...
PGDATABASE=...
PGSSLMODE=disable

# Auth
JWT_SECRET=...           # 필수
JWT_ACCESS_TTL=15m
JWT_REFRESH_TTL=168h
ALLOW_SIGNUP=false
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=Lax
AUTH_COOKIE_DOMAIN=
AUTH_COOKIE_PATH=/
CORS_ALLOWED_ORIGINS=https://example.com,https://app.example.com
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
// AlertService에서 goroutine으로 호출
threadTS, _ := s.slackClient.GetThreadTS(alert.Fingerprint)
go s.agentService.RequestAnalysis(alert, threadTS)
```

### Alert Status Colors
- critical: `#dc3545` (red)
- warning: `#ffc107` (yellow)
- resolved: `#36a64f` (green)
- default: `#17a2b8` (blue)

## Dependencies

- `gin-gonic/gin` - HTTP router
- `jackc/pgx/v5` - PostgreSQL driver
- `github.com/golang-jwt/jwt/v5` - JWT auth
- `google.golang.org/genai` - Gemini embeddings
- `pgvector-go` - Vector insert for PostgreSQL
- Go 1.24+
