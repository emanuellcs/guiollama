# Architecture

GUIOllama is built using **Clean Architecture** patterns. The codebase is organized concentrically, with domain entities at the center and external concerns (UI, Database, APIs) at the edge.

## Directory Structure

- **`domain/`**: The innermost layer. Contains interfaces (Ports), Entities, and Value Objects. Nothing here imports from outside.
- **`services/`**: Use cases and business logic. Coordinates fetching data from interfaces and returning it to the UI. Depends only on `domain/`.
- **`adapters/`**: The outer layer implementation of domain interfaces. Contains the Ollama API client, SQLite/SQLAlchemy repositories, and file storage mechanisms.
- **`ui/`**: Chainlit event handlers, state management, and view logic. The UI layer calls the `services/` layer and never accesses adapters or database models directly.
- **`infra/`**: Infrastructure-level concerns like logging configuration, application settings (Pydantic), and observability metrics.
- **`app/`**: The composition root. This is where dependency injection is configured. Adapters are instantiated and passed into services here.
- **`utils/`**: Generic helpers that are not domain-specific.
