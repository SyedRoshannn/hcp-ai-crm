# System Architecture

This document details the architectural layout, data flow pipelines, and execution routing for the HCP AI CRM Assistant.

---

## Overall System Architecture

The project is built on a split-screen single page layout connected to a stateful REST backend using FastAPI and LangGraph:

```mermaid
flowchart TD
    subgraph Frontend["Frontend (React + Redux)"]
        UI[React App UI]
        ReduxStore[Redux Store]
        STT[Web Speech STT]
    end

    subgraph Backend["Backend (FastAPI + LangGraph)"]
        API[FastAPI Endpoints]
        Workflow[LangGraph Workflow]
        State[Agent State]
        Classification[Intent Classifier]
        ResponseService[Response Generator]
    end

    subgraph DB["Database Layer"]
        Repo[Repositories]
        Postgres[("PostgreSQL DB")]
    end

    UI <-->|Redux State Sync| ReduxStore
    STT -->|Transcript| UI
    UI <-->|REST HTTP /chat| API
    API <-->|Orchestrates| Workflow
    Workflow <-->|Maintains| State
    Workflow <-->|Intent Matching| Classification
    Workflow <-->|Generates Natural Summary| ResponseService
    Workflow <-->|CRUD Operations| Repo
    Repo <-->|SQL Queries| Postgres
```

---

## Core Layers Description

### 1. Presentation Layer (React + Redux)
- **React Components**: Splits viewport into left-side read-only form cards ([InteractionForm.jsx](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/components/InteractionForm/InteractionForm.jsx)) and right-side interactive workspace ([ChatPanel.jsx](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/components/ChatPanel/ChatPanel.jsx)).
- **Redux Slice Store**: Synchronizes interaction IDs, form state extractions, memory metadata, and loading statuses in a single unified state manager ([interactionSlice.js](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/redux/interactionSlice.js)).

### 2. Service Orchestration Layer (FastAPI + LangGraph)
- **FastAPI Router**: Listens on POST `/chat`, parses inputs, loads context, and triggers the asynchronous LangGraph execution block.
- **LangGraph StateGraph**: Models the agent's workflow as a directed graph. The state structure represents a memory buffer that flows between Intent Router, Tool Executions, and Response Nodes.

### 3. Data Persistence Layer (SQLAlchemy + Repository + PostgreSQL)
- **SQLAlchemy Models**: Defines DB entities mapped cleanly to PostgreSQL schemas. Includes dynamic datatype bindings for JSON array structures.
- **Repository Pattern**: Encapsulates DB logic inside `InteractionRepository`, protecting caller service loops from SQL driver changes.

---

## Detailed Data Flows

### Request-Response Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant LangGraph
    participant Database

    User->>Frontend: Speaks or types query
    Frontend->>FastAPI: POST /chat (text + current form state + active id)
    FastAPI->>LangGraph: Initialize State and Run Graph
    LangGraph->>LangGraph: intent_router (Classify Intent)
    Alt Intent = LOG/EDIT/FOLLOWUP
        LangGraph->>Database: Execute Tool CRUD Action
        Database-->>LangGraph: Return Record
    End
    LangGraph->>LangGraph: response_node (Format natural AI description)
    LangGraph-->>FastAPI: Return final State Graph properties
    FastAPI-->>Frontend: HTTP 200 (AI text + updated form + id)
    Frontend->>Frontend: Dispatch to Redux Store
    Frontend-->>User: Animate updated fields & print AI reply
```

### LangGraph Workflow & Tool Routing
```mermaid
flowchart TD
    Start([Start Endpoint Request]) --> RouterNode[router_node: Classify intent via LLM]
    RouterNode --> RoutingBranch{Conditional Edge: Intent}
    
    RoutingBranch -->|LOG_INTERACTION| LogTool[log_interaction_tool]
    RoutingBranch -->|EDIT_INTERACTION| EditTool[edit_interaction_tool]
    RoutingBranch -->|FOLLOW_UP| FollowUpTool[follow_up_tool]
    RoutingBranch -->|VOICE_SUMMARY| VoiceTool[voice_summary_tool]
    RoutingBranch -->|MATERIAL_RECOMMENDATION| MatTool[material_recommendation_tool]
    RoutingBranch -->|HISTORY_SEARCH| HistoryTool[history_search_tool]
    RoutingBranch -->|UNKNOWN / CHAT| ResponseNode[response_node: Format conversational reply]

    LogTool --> ResponseNode
    EditTool --> ResponseNode
    FollowUpTool --> ResponseNode
    VoiceTool --> ResponseNode
    MatTool --> ResponseNode
    HistoryTool --> ResponseNode

    ResponseNode --> End([Return Payload to FastAPI])
```
