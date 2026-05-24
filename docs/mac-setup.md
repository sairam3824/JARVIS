# macOS Setup Guide

## Requirements

- macOS with microphone access enabled for the browser
- Python 3.12+ or conda
- Node.js 22+
- Docker Desktop (optional)
- OpenAI API key, optional Anthropic API key

## Native Setup

```bash
cp .env.example .env
./scripts/bootstrap.sh
./scripts/dev.sh
```

## Docker Setup

```bash
cp .env.example .env
docker compose up --build
```

## Notes

- Safari and Chrome both work, but Chrome generally gives smoother Web Audio behavior.
- If microphone access is blocked, reset permissions in System Settings > Privacy & Security > Microphone.
- The backend stores local state in `backend/data/`.

