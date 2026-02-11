# GUIOllama

GUIOllama is a production-grade, highly modular Chainlit frontend client for Ollama. It provides a desktop-like experience delivered as a robust web application, enabling chat, model management, RAG workflows, and agentic tool integrations for local LLMs.

## Features (Roadmap)
- **Chat & Conversation UX**: Multi-session management, streaming, branch conversations.
- **Model Management**: Pull, inspect, and manage local Ollama models.
- **Prompt Library**: Save, template, and version system prompts.
- **RAG**: Local document ingestion and vector retrieval.
- **Tools**: Agentic workflows with strict permissioning.
- **Observability**: Tracing, metrics, and structured local logging.

## Architecture
GUIOllama strictly follows Clean Architecture principles to ensure maintainability, testability, and clear separation of concerns.
See `docs/architecture.md` for more details.

## Quickstart (Docker)

1. Clone the repository.
2. Run `docker-compose up -d`.
3. Open `http://localhost:8000` in your browser.

*Note: This spins up both GUIOllama and a local Ollama instance. If you already have Ollama running, adjust `.env` and `docker-compose.yml` accordingly.*

## Local Development Setup

1. Requires Python 3.11+.
2. `make install`
3. `cp .env.example .env` (update `OLLAMA_BASE_URL` if needed).
4. `make dev`

Access the UI at `http://localhost:8000`.
