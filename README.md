# Website & App Builder Agent

A free, local-first website and app builder that turns a short prompt into a structured app specification and preview UI.

## Features
- Prompt-driven app classification
- FastAPI backend with /api/health and /api/build
- React + Vite frontend for previewing generated app specs
- Public free API enrichment for city and weather data
- No paid API keys required for the baseline MVP

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Then open the app at:

```text
http://localhost:5173
```

## Health check

```bash
curl http://localhost:8000/api/health
```

## Build endpoint example

```bash
curl -X POST http://localhost:8000/api/build \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a modern fintech landing page","tone":"premium","style":"dark"}'
```

## URLs
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Optional local Ollama setup

If you want to connect to a local LLM later:

```bash
ollama pull llama3.1
```

Then configure the model in `.env` or your local environment using the values in `.env.example`.

## Testing

```bash
cd backend
python -m pytest
```

## Project structure

```text
website-app-builder-agent/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
├── tests/
│   └── backend/
│       └── test_api.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md
├── .env.example
├── .gitignore
├── README.md
├── start.sh
└── .github/ (optional future GitHub configuration)
```
