---
name: kube-rca-backend
description: |
  Use when working on Go backend code for kube-rca project.
  Triggers: Alertmanager webhook, Slack client, alert processing,
  Go API development, gin framework, internal/ directory, go.mod changes,
  handler/service/client/model layers, thread management.
---

# Kube-RCA Backend

Go-based backend service for Kubernetes Root Cause Analysis.
Receives Alertmanager webhooks and forwards alerts to Slack with thread management.

## Project Structure

```
backend/
├── main.go                      # Entry point, DI setup, router config
├── internal/
│   ├── handler/
│   │   ├── alert.go             # POST /webhook/alertmanager
│   │   └── health.go            # GET /ping, GET /
│   ├── service/
│   │   └── alert.go             # Alert filtering, business logic
│   ├── client/
│   │   ├── slack.go             # Slack API client, thread management
│   │   └── slack_alert.go       # Alert-specific Slack formatting
│   └── model/
│       └── alert.go             # AlertmanagerWebhook, Alert structs
├── go.mod
└── Dockerfile
```

## Architecture Pattern

**Dependency Flow**: `handler → service → client`

**Initialization Order**: `client → service → handler`

## Key Components

### Alertmanager Webhook Handler
- Endpoint: `POST /webhook/alertmanager`
- Parses AlertmanagerWebhook JSON payload
- Delegates to AlertService for processing

### Alert Service
- Filters alerts (shouldSendToSlack)
- Coordinates with SlackClient for delivery
- Returns sent/failed counts

### Slack Client
- Uses Bot Token (not webhook) for thread_ts support
- Manages fingerprint → thread_ts mapping via sync.Map
- Enables threaded conversations for firing/resolved alerts

## Environment Variables

```bash
SLACK_BOT_TOKEN=xoxb-...    # Slack Bot Token
SLACK_CHANNEL_ID=C...       # Target channel ID
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

### Alert Status Colors
- critical: `#dc3545` (red)
- warning: `#ffc107` (yellow)
- resolved: `#36a64f` (green)

## Dependencies

- `gin-gonic/gin` - HTTP router
- Go 1.22+

## Future Plans

- AI-based Root Cause Analysis integration
- K8s client for cluster state inspection
