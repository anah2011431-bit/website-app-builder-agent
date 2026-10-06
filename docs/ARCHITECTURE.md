# Website & App Builder Agent Architecture

This repository currently follows a simple MVP architecture that keeps the system easy to reason about and easy to extend.

```text
React / Vite
    ↓
FastAPI backend
    ↓
Build endpoint
    ↓
App specification
    ↓
Frontend preview
```

## Components

### React / Vite frontend
The frontend provides a simple user experience with:
- prompt input
- loading state
- API error handling
- generated app specification display
- preview card layout

### FastAPI backend
The backend handles:
- health checks
- incoming prompt payloads
- app-type classification
- optional city/weather enrichment using public free APIs
- response generation based on a simple template system

### Build endpoint
The `/api/build` route accepts a prompt and returns a structured JSON specification containing:
- title
- app type
- theme
- pages
- sections
- hero headline and copy
- optional location info

### Frontend preview
The frontend renders the generated specification into a lightweight previews panel so the user can immediately inspect the generated idea without needing a full project scaffold yet.

## Why this architecture
This structure is intentionally minimal and supports the next phase of work without forcing a complex stack too early. It is easy to test, easy to run locally, and safe to evolve into a more advanced generator.
