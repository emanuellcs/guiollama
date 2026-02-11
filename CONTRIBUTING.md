# Contributing to GUIOllama

Thank you for your interest in contributing! This document outlines the process for contributing to GUIOllama.

## Architecture

We follow a strict Clean Architecture approach:
- `domain/`: Interfaces, entities, and value objects. No dependencies on outer layers.
- `services/`: Business logic and use cases. Depends only on `domain/`.
- `adapters/`: Implementations of domain interfaces (Ollama client, Database).
- `ui/`: Chainlit presentation layer.
- `infra/`: Logging, config, and telemetry.
- `app/`: Composition root / Dependency Injection container.

Please ensure your contributions respect these boundaries. Business logic should not live in the `ui/` handlers.

## Development Setup

1. Clone the repository.
2. Run `make install` to set up your environment (requires Python 3.11+).
3. Copy `.env.example` to `.env` and adjust as necessary.
4. Run `make dev` to start the local development server.

## Code Quality

- We use `ruff` for linting and formatting. Run `make lint`.
- We use `mypy` for strict type checking.
- Ensure all new features are covered by unit tests (`make test`).

## Pull Requests

1. Create a branch using Conventional Commits naming conventions if possible (e.g., `feat/ui-updates`).
2. Write tests for your changes.
3. Submit a PR describing the problem solved and the approach taken.
