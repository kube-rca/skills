---
name: kube-rca-frontend
description: |
  Use when working on frontend code for kube-rca project.
  Triggers: React components, UI development, dashboard,
  alert visualization, frontend/ directory changes.
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
├── vite.config.ts
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── types.ts
    ├── components/
    │   ├── RCATable.tsx
    │   ├── TimeRangeSelector.tsx
    │   └── Pagination.tsx
    ├── constants/
    │   └── index.ts
    └── utils/
        ├── api.ts
        ├── filterAlerts.ts
        └── mockData.ts
```

## Key UI Flow

- `App.tsx` loads RCA list via `fetchRCAs()` and paginates results.
- If fetch fails in dev mode, `mockData.ts` provides fallback rows.
- `filterAlerts.ts` filters rows by time range selection.

## API Integration

- Base URL: `VITE_API_BASE_URL` or fallback
  - dev: `http://localhost:8080`
  - prod: `http://kube-rca-backend:8080`
- Endpoints used in `src/utils/api.ts`:
  - `GET /api/rca`
  - `GET /api/rca/:id`

If backend responses differ, update `src/utils/api.ts` parsing logic.

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
