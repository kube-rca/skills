---
name: kube-rca-frontend
description: |
  Use when working on frontend code for kube-rca project.
  Triggers: React components, UI development, dashboard,
  auth/login flow, alert visualization, frontend/ directory changes.
---

# Kube-RCA Frontend

Frontend application for Kubernetes Root Cause Analysis (RCA) dashboard.

## Project Structure

```
frontend/
├── Dockerfile
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── types.ts
    ├── components/
    │   ├── AuthPanel.tsx
    │   ├── RCADetailView.tsx
    │   ├── RCATable.tsx
    │   ├── TimeRangeSelector.tsx
    │   └── Pagination.tsx
    ├── constants/
    │   └── index.ts
    └── utils/
        ├── api.ts
        ├── auth.ts
        ├── config.ts
        └── filterAlerts.ts
```

## Key UI Flow

- `App.tsx` 시작 시 `/api/v1/auth/config`와 `/api/v1/auth/refresh`로 인증 상태를 초기화합니다.
- 인증 전에는 `AuthPanel`에서 로그인/회원가입을 수행합니다.
- 인증 후 `fetchRCAs()`로 Incident 목록을 로딩하고 상세 화면(`RCADetailView`)을 제공합니다.
- 401 응답 시 refresh 토큰으로 1회 재시도합니다.

## API Integration

- Base URL: `VITE_API_BASE_URL` (없으면 동일 오리진 `''` 사용)
- Endpoints used in `src/utils/*.ts`:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/config`
  - `GET /api/v1/incidents`
  - `GET /api/v1/incidents/:id`
  - `PUT /api/v1/incidents/:id`

`requestWithAuth`가 `Authorization: Bearer <token>` 헤더와 `credentials: include`를 사용합니다.

## Environment Variables

```bash
VITE_API_BASE_URL=http://kube-rca-backend:8080
```

## Development Commands

```bash
cd frontend && npm ci
cd frontend && npm run dev
cd frontend && npm run build && npm run lint
```
