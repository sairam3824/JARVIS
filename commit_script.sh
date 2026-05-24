#!/bin/bash

# Initialize and configure
git config --local user.name "sairam3824"
git config --local user.email "sairam3824@users.noreply.github.com"

# Commit 1
git add .gitignore README.md LICENSE torun.txt
git commit -m "docs: Initial project documentation and configuration"

# Commit 2
git add docker-compose.yml docker/ .env.example
git commit -m "build: Add Docker and environment configuration templates"

# Commit 3
git add backend/requirements.txt backend/pyproject.toml
git commit -m "build(backend): Configure backend Python dependencies"

# Commit 4
git add backend/tests/
git commit -m "test(backend): Setup backend test infrastructure"

# Commit 5
git add backend/data/
git commit -m "chore(backend): Initialize backend data directory structure"

# Commit 6
git add backend/app/
git commit -m "feat(backend): Implement core backend application structure"

# Commit 7
git add frontend/package.json frontend/package-lock.json frontend/tsconfig.* frontend/vite.config.* frontend/tailwind.config.* frontend/postcss.config.js
git commit -m "build(frontend): Configure React frontend environment and dependencies"

# Commit 8
git add frontend/src/ frontend/index.html frontend/dist/ frontend/node_modules/
git commit -m "feat(frontend): Implement frontend UI structure and build artifacts"

# Commit 9
git add agents/__init__.py agents/memory.py agents/policies.py
git commit -m "feat(agents): Setup agent memory and base policies"

# Commit 10
git add agents/orchestrator.py agents/planner.py
git commit -m "feat(agents): Implement agent orchestrator and planner modules"

# Commit 11
git add tools/registry.py tools/base.py tools/__init__.py
git commit -m "feat(tools): Create tool registry and base abstractions"

# Commit 12
git add tools/implementations/ tools/policies/
git commit -m "feat(tools): Add specific tool implementations and policies"

# Commit 13
git add models/
git commit -m "feat(models): Define model architecture and schemas"

# Commit 14
git add scripts/
git commit -m "chore(scripts): Add utility and deployment scripts"

# Commit 15
git add docs/
git commit -m "docs: Add detailed project documentation"

# Commit 16
git add animations/
git commit -m "feat(ui): Add UI animations and assets"

# Commit 17
git add .claude/
git commit -m "chore: Add IDE specific configuration"

# Commit 18 (Catch all for any missed files)
git add .
git commit -m "chore: Finalize project structure and missed configuration files"

# Remote and Push
git remote add origin https://github.com/sairam3824/JARVIS.git
git branch -M main
git push -u origin main
