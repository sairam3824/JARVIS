# JARVIS Architecture

## Layers

- `backend/app/api`: thin HTTP and WebSocket routing
- `backend/app/services`: application orchestration and integration services
- `backend/app/providers`: OpenRouter-backed LLM and speech adapters
- `backend/app/repositories`: SQLite persistence
- `agents/`: domain orchestration, memory assembly, policy prompts
- `tools/`: guarded tool contracts and implementations
- `models/`: shared Python contracts and event schemas
- `frontend/src`: HUD interface, scenes, stores, services, hooks
- `animations/`: shared visual presets and scene constants

## Data Flow

1. Frontend sends text or voice input.
2. Backend classifies intent, selects the model route, and assembles memory context.
3. `AgentOrchestrator` optionally executes tools, planner logic, and workspace services before streaming provider output.
4. Repositories persist chats, tool traces, memory facts, datasets, plans, QR history, and integration snapshots.
5. WebSocket events update the chat transcript, process lane, tool rail, and system dashboard.

## Safety

- File and terminal tools are scoped by `JARVIS_ALLOWED_ROOTS`.
- Mutating tools expose `requires_confirmation`.
- Terminal and code execution use timeouts and output truncation.
- Desktop automation is app-specific and relies on explicit launch/open flows rather than arbitrary screen control.
