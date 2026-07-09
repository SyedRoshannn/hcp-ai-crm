# Project Folder Structure

This document outlines the codebase directories, file structures, and responsibilities for both frontend and backend modules.

---

## Folder Tree

```text
hcp-ai-crm/
├── backend/                    # FastAPI Backend Module
│   ├── alembic/                # Database Migrations Repository
│   │   └── versions/           # Python migration version scripts
│   ├── app/                    # Primary application package
│   │   ├── api/                # HTTP API Endpoint Controllers
│   │   │   └── chat.py         # POST /chat route controller
│   │   ├── core/               # Configuration settings and env loaders
│   │   ├── db/                 # DB engines and session managers
│   │   ├── langgraph/          # LangGraph Agent orchestration
│   │   │   ├── nodes.py        # Graph node execution blocks
│   │   │   ├── state.py        # Schema defining agent state
│   │   │   ├── workflow.py     # Graph builder and compiler
│   │   │   └── tools/          # AI Tool execution units
│   │   ├── models/             # SQLAlchemy ORM Data Models
│   │   │   └── interaction.py  # HCP Interaction table model
│   │   ├── repositories/       # Database Repository layer
│   │   │   └── interaction_repository.py # CRUD controller
│   │   ├── schemas/            # Pydantic Schemas for validation
│   │   └── services/           # Business logic & response systems
│   │       ├── interaction_service.py # Extraction and formatting logic
│   │       └── response_service.py # Generational LLM summaries
│   └── tests/                  # Backend unit and integration tests
├── frontend/                   # React Frontend Module
│   ├── src/                    # Source files
│   │   ├── components/         # Presentation UI Components
│   │   │   ├── ChatPanel/      # Conversational Chat controller
│   │   │   └── InteractionForm/# HCP Form renderer
│   │   ├── redux/              # Redux slices and store config
│   │   ├── services/           # Client HTTP API connections
│   │   └── styles/             # Global CSS layout files
│   └── vite.config.js          # Vite build config
```

---

## Folder Responsibilities

### 1. `backend/app/api/`
Handles REST interfaces. Defines route definitions, parses incoming HTTP bodies into validated Pydantic models, and returns structured API responses.

### 2. `backend/app/db/`
Maintains SQLAlchemy database connections, initializes the connection pool engine, and exports the `SessionLocal` generator dependency injection.

### 3. `backend/app/models/`
Defines ORM database schemas. The `Interaction` model maps attributes (including list types as JSON columns) to the PostgreSQL database table structures.

### 4. `backend/app/repositories/`
Implements the Repository Pattern. Encapsulates raw SQLAlchemy database query routines (e.g. `create_interaction`, `search`, `update`) to separate DB execution loops from routing controllers.

### 5. `backend/app/langgraph/`
Handles AI workflow loops:
- `workflow.py` constructs the stateful graph loop.
- `state.py` defines the variables matching state models.
- `nodes.py` houses logic for Intent classification routing and conversational response generation.

### 6. `backend/app/langgraph/tools/`
Houses the execution blocks for the AI agent's tools:
- `log_interaction_tool.py`: Commits new extractions to the DB.
- `edit_interaction_tool.py`: Merges and saves revisions to the DB.
- `follow_up_tool.py`: Appends, updates, or deletes follow-ups.
- `voice_summary_tool.py`: Process transcripts for summarization.
- `material_recommendation_tool.py`: Evaluates and filters catalog guides.
- `history_search_tool.py`: Resolves natural history query filter clauses.

### 7. `backend/app/services/`
Executes parsing and generation tasks. `response_service.py` runs Groq chains translating status logs into friendly summaries, while `interaction_service.py` extracts entity variables.

### 8. `backend/tests/`
Automated test suite. Tests routes, state validations, repository patterns, and full end-to-end intent routes.
