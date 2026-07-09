# Feature Documentation

This document describes every user-facing and backend feature implemented in the HCP AI CRM Assistant.

---

## 1. Log Interaction

- **Purpose**: Parses meeting transcripts/notes and creates new HCP interaction records.
- **How it Works**: Classifies log intent, passes user input to `extract_interaction_details`, saves the record to PostgreSQL, and returns the generated UUID.
- **Files Involved**:
  - [log_interaction_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/log_interaction_tool.py)
  - [interaction_repository.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/repositories/interaction_repository.py)
- **Example Prompt**: *"Met Dr. Smith today to discuss Product X, positive sentiment, shared brochure"*
- **Current Status**: **Fully Working**. Persists records immediately and synchronizes state with the frontend.

---

## 2. Edit Interaction

- **Purpose**: Modifies an active interaction's properties using natural language instructions.
- **How it Works**: Identifies the current interaction ID from the state, fetches updates, merges new parameters with old ones (preserving unchanged columns), and saves to PostgreSQL.
- **Files Involved**:
  - [edit_interaction_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/edit_interaction_tool.py)
  - [interaction_repository.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/repositories/interaction_repository.py)
- **Example Prompt**: *"Change the doctor's name to Dr. John Smith"*
- **Current Status**: **Fully Working**. Resolves column updates dynamically.

---

## 3. Voice Summary

- **Purpose**: Processes unstructured verbal narratives to populate interaction fields.
- **How it Works**: Cleans voice note commands, extracts parameters, writes the interaction to the DB, and fills the left-hand form.
- **Files Involved**:
  - [voice_summary_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/voice_summary_tool.py)
- **Example Prompt**: *"Summarize this voice note: Met Dr. Alice, positive response, samples distributed: 10 units."*
- **Current Status**: **Fully Working**.

---

## 4. Material Recommendation

- **Purpose**: Suggests relevant product materials to attach to the log.
- **How it Works**: Extract therapeutic areas or product names from query requests, matches them against the catalog registry, and outputs recommendations.
- **Files Involved**:
  - [material_recommendation_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/material_recommendation_tool.py)
- **Example Prompt**: *"What materials can I share for diabetes?"*
- **Current Status**: **Fully Working**.

---

## 5. Follow-up scheduler

- **Purpose**: Manages follow-up actions associated with HCP interactions.
- **How it Works**: Evaluates request intent (ADD, UPDATE, REMOVE, VIEW, CLARIFY), alters the list representation, and updates the database row.
- **Files Involved**:
  - [follow_up_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/follow_up_tool.py)
- **Example Prompt**: *"Schedule a follow up call next Monday"*
- **Current Status**: **Fully Working**.

---

## 6. Conversation Memory & Context Management

- **Purpose**: Resolves context tracking across multiple chat turns (like ChatGPT).
- **How it Works**: Preserves interaction ID, last intent, and last tool parameters in the Redux store, propagating them back to the `/chat` route in subsequent requests.
- **Files Involved**:
  - [context_manager.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/utils/context_manager.py)
  - [interactionSlice.js](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/redux/interactionSlice.js)
  - [ChatPanel.jsx](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/components/ChatPanel/ChatPanel.jsx)
- **Current Status**: **Fully Working**. Supports context resolution for edits and follow-ups.

---

## 7. AI History Search

- **Purpose**: Queries past interactions from the database using natural language queries.
- **How it Works**: Translates conversational queries into filters, searches PostgreSQL, and returns formatted logs.
- **Files Involved**:
  - [history_search_tool.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/tools/history_search_tool.py)
  - [interaction_repository.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/repositories/interaction_repository.py)
- **Example Prompt**: *"Show meetings with Dr. Smith"*
- **Current Status**: **Fully Working**. Matches terms and filters dynamically.

---

## 8. AI Response Generation

- **Purpose**: Generates natural, context-aware conversational summaries instead of robotic statements.
- **How it Works**: Feeds the current state into an LLM response service to synthesize status strings into friendly paragraphs.
- **Files Involved**:
  - [response_service.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/services/response_service.py)
  - [nodes.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/langgraph/nodes.py)
- **Current Status**: **Fully Working**.

---

## 9. Speech-to-Text (STT) Voice Input

- **Purpose**: Captures user speech directly in the browser to populate the chat input.
- **How it Works**: Incorporates browser-native Web Speech API. Clicking the microphone starts recording (indicated by a pulse animation), updates the text input live, and auto-submits on completion.
- **Files Involved**:
  - [ChatPanel.jsx](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/components/ChatPanel/ChatPanel.jsx)
  - [index.css](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/frontend/src/styles/index.css)
- **Current Status**: **Fully Working** on browsers supporting SpeechRecognition.

---

## 10. PostgreSQL Engine & Type Compatibility

- **Purpose**: Replaces SQLite with a robust database engine.
- **How it Works**: Leverages PostgreSQL through connection URL environment loading and SQLAlchemy model definition type casts for JSON array queries.
- **Files Involved**:
  - [database.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/db/database.py)
  - [env.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/alembic/env.py)
  - [interaction_repository.py](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/app/repositories/interaction_repository.py)
- **Current Status**: **Fully Working** and verified across all tests.
