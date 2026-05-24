# JARVIS

JARVIS is a local-first AI assistant with a FastAPI backend, a React + Vite frontend, WebSocket streaming, SQLite-backed memory, and a modular tool system for analytics, planning, QR workflows, smart-home status, and guarded desktop actions.

The codebase is organized as a full-stack assistant product rather than a single demo endpoint:

- Text chat and voice chat share the same orchestration pipeline.
- Tool use is planned before the model answers.
- Conversations, memory, tool traces, datasets, planner previews, QR history, and integration snapshots are stored locally in SQLite.
- The frontend exposes both a cinematic chat HUD and a live system dashboard.

## Highlights

- FastAPI backend with REST routes and two WebSocket streams
- React 18 + TypeScript + Vite frontend with Tailwind, Framer Motion, and Three.js
- OpenRouter-backed chat, speech-to-text, and text-to-speech
- Local tool registry with safety flags for filesystem, terminal, code execution, and macOS app launching
- Workspace modules for analytics, vision, planning, QR generation/scanning, and Home Assistant status
- SQLite persistence for conversation history, memory, traces, and workspace artifacts
- Unit tests for backend orchestration, routing, providers, and frontend hooks

## Architecture

### Request flow

1. The frontend sends a chat message, voice clip, or workspace request.
2. FastAPI routes the request into a service layer.
3. `AgentOrchestrator` classifies intent, selects the provider route, assembles memory, and creates a tool plan.
4. Planned tools run through `ToolRegistry` and their outputs are recorded.
5. The provider produces the final answer, which is stored in SQLite and streamed back to the UI when applicable.

### Main layers

- `backend/app/api/`: REST and WebSocket routes
- `backend/app/services/`: application services and integrations
- `backend/app/services/intelligence/`: analytics, planning, sentiment, vision, task routing, audio features
- `backend/app/providers/`: LLM and audio provider adapters
- `backend/app/repositories/`: SQLite persistence
- `agents/`: orchestration, planning, memory assembly, prompt policy
- `tools/`: tool contracts, registry, safety policy, implementations
- `models/`: shared Pydantic models and event contracts
- `frontend/src/`: pages, components, hooks, stores, scenes, tests
- `docs/`: architecture and local setup notes

### Safety model

JARVIS separates safe tools from confirm-required tools:

- Safe by default: analytics, sentiment, memory store, QR, weather, Home Assistant status
- Confirmation-oriented tools: filesystem reads, terminal execution, Python code execution, macOS app launch
- Filesystem access is scoped by `JARVIS_ALLOWED_ROOTS`
- Terminal and code execution are time-limited via `TERMINAL_TIMEOUT_SECONDS`

## Feature set

### Assistant capabilities

- Text chat over REST and WebSocket
- Voice transcription and TTS reply generation
- Intent classification and model routing
- Local memory recall from prior conversations
- Tool planning from either explicit prefixes or model/heuristic planning

### Workspace capabilities

- Analytics Studio: ingest CSV, manual tabular text, or `.xlsx` files and compute summary statistics
- Visual Search: inspect image dimensions, dominant color, brightness, and simple tags
- Planner Workspace: generate checklist, schedule, template, and recipe previews
- QR Lab: generate QR codes and scan uploaded QR images
- Smart Home monitor: fetch Home Assistant device state snapshots
- Template drafts: store reusable generated planner/template outputs in SQLite

### Supported prompt prefixes

The tool router supports explicit prefixes for power users:

- `web:`
- `file:`
- `run:`
- `python:`
- `remember:`
- `analytics:`
- `launch:`
- `checklist:`
- `weather:`
- `sentiment:`
- `qr:`
- `home:`

## Tech stack

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic / pydantic-settings
- SQLite
- `httpx`
- `psutil`
- `pillow`
- `opencv-python-headless`
- `openpyxl`
- `qrcode`

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Three.js / React Three Fiber
- Zustand

### AI and integrations

- OpenRouter chat model via `OPENROUTER_MODEL`
- OpenRouter audio model via `OPENROUTER_AUDIO_MODEL`
- Optional Home Assistant integration
- macOS desktop automation through the native `open` command

## Project structure

```text
.
├── agents/                  # Orchestration, planning, memory assembly, prompt policy
├── animations/              # Shared frontend animation presets
├── backend/
│   ├── app/
│   │   ├── api/             # REST and WebSocket routes
│   │   ├── core/            # Config, dependency wiring, logging
│   │   ├── providers/       # OpenRouter adapter
│   │   ├── repositories/    # SQLite persistence
│   │   ├── schemas/         # API request/response models
│   │   └── services/        # Chat, voice, system, workspace, intelligence, integrations
│   ├── data/                # Local SQLite database storage
│   └── tests/               # Backend tests
├── docs/                    # Architecture and setup notes
├── frontend/
│   ├── src/
│   │   ├── app/             # Route shell
│   │   ├── components/      # Chat, dashboard, workspace, UI components
│   │   ├── hooks/           # WebSocket and voice hooks
│   │   ├── pages/           # Landing, chat, dashboard
│   │   ├── scenes/          # Three.js scene(s)
│   │   ├── services/        # API client helpers
│   │   ├── stores/          # Zustand stores
│   │   └── test/            # Frontend tests
│   └── package.json
├── models/                  # Shared contracts and event payloads
├── scripts/                 # Bootstrap and dev scripts
└── tools/                   # Tool registry, policies, implementations
```

## API surface

### REST endpoints

- `GET /health`: service health check
- `POST /chat`: request a text completion
- `POST /voice`: upload audio and receive transcript + reply + optional TTS audio
- `GET /tools`: list registered tool definitions
- `GET /system`: fetch system metrics and recent tool trace summary
- `POST /ingest/data`: ingest a dataset for analytics
- `POST /vision/analyze`: analyze an uploaded image
- `POST /planner/preview`: build a planning/template/recipe preview
- `POST /qr`: generate or scan a QR code
- `GET /integrations/home-assistant/status`: fetch Home Assistant summary

### WebSocket endpoints

- `/ws/chat`: streams session, intent, model, tool, and assistant delta events
- `/ws/system`: streams periodic system snapshots

## Environment variables

Copy `.env.example` to `.env` and fill in what you need.

### Required for full assistant behavior

- `OPENROUTER_API_KEY`: enables chat, transcription, and TTS

### Common settings

- `OPENROUTER_MODEL`: default chat model
- `OPENROUTER_AUDIO_MODEL`: audio transcription/TTS model
- `TTS_VOICE`: voice name for synthesized speech
- `DATABASE_URL`: SQLite location, default `sqlite:///backend/data/jarvis.db`
- `JARVIS_ALLOWED_ROOTS`: comma-separated safe roots for file access
- `TERMINAL_TIMEOUT_SECONDS`: timeout for terminal/code tools
- `CORS_ORIGIN`: frontend origin
- `LOG_LEVEL`: backend log level
- `VITE_API_BASE`: frontend API base URL

### Optional integrations

- `HOME_ASSISTANT_URL`
- `HOME_ASSISTANT_TOKEN`

If `OPENROUTER_API_KEY` is missing, the app still boots, but model-backed chat/voice functionality returns configuration messages instead of live AI output.

## Getting started

### Option 1: quick local bootstrap

```bash
cp .env.example .env
./scripts/bootstrap.sh
./scripts/dev.sh
```

This is the fastest path, but note that `bootstrap.sh` installs Python dependencies into your current Python environment.

### Option 2: recommended isolated local setup

```bash
cp .env.example .env
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
./scripts/dev.sh
```

### Option 3: Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

### Local URLs

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Development

### Backend

Run the API manually:

```bash
cd backend
PYTHONPATH="$(pwd)/.." uvicorn app.main:app --reload --port 8000
```

Run backend tests:

```bash
cd backend
pytest
```

### Frontend

Run the frontend manually:

```bash
cd frontend
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

Run frontend tests:

```bash
cd frontend
npm test
```

## Data and persistence

By default, runtime data is stored locally in `backend/data/jarvis.db`.

The database schema covers:

- conversation messages
- memory records
- tool traces
- datasets
- analysis runs
- planner previews
- QR history
- integration snapshots
- template entries

This makes the repo convenient for local experimentation, but it also means assistant state is persisted between runs unless you change `DATABASE_URL`.

## Notes for contributors

- The current backend provider wiring is OpenRouter-only.
- The planner supports both explicit tool prefixes and inferred tool usage.
- The system dashboard reads live metrics from `/system` and `/ws/system`.
- Home Assistant support is read-only.
- macOS desktop automation is implemented with the `open` command and is intended for local workstation use.

## Documentation

- [Architecture notes](docs/architecture.md)
- [macOS setup guide](docs/mac-setup.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
