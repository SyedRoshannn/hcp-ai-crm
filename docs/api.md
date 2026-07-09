# API Documentation

This document describes the REST API endpoints and data contracts for the HCP AI CRM backend.

---

## Base URL
The backend server listens locally at:
`http://127.0.0.1:8000`

---

## Endpoints Index

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | Root verification endpoint. Returns project name status. |
| **GET** | `/health` | Health check endpoint. |
| **POST** | `/chat` | Main conversational assistant endpoint. Orchestrates LangGraph agent tasks. |

---

## Detailed Endpoint Contracts

### 1. Root API Endpoint
- **URL**: `/`
- **Method**: `GET`
- **Response Content-Type**: `application/json`
- **Status Codes**:
  - `200 OK`
- **Example Response**:
  ```json
  {
    "status": "running",
    "project": "HCP AI CRM"
  }
  ```

---

### 2. Health Check Endpoint
- **URL**: `/health`
- **Method**: `GET`
- **Response Content-Type**: `application/json`
- **Status Codes**:
  - `200 OK`
- **Example Response**:
  ```json
  {
    "backend": "healthy"
  }
  ```

---

### 3. Assistant Chat Endpoint
- **URL**: `/chat`
- **Method**: `POST`
- **Request Content-Type**: `application/json`
- **Status Codes**:
  - `200 OK` (Successful parsing and agent loop execution)
  - `422 Unprocessable Entity` (Invalid JSON body parameters)
  - `500 Internal Server Error` (Unexpected database or LLM connection failures)

#### Request Schema (Pydantic model `ChatRequest`)
- `message` (string, required): The user query, instruction, or voice note transcript.
- `extracted_data` (object, required): The current form state dictionary displayed in the frontend.
- `interaction_id` (string/null, optional): UUID of the active logged interaction.
- `last_intent` (string/null, optional): Intent of the preceding chat turn.
- `last_tool` (string/null, optional): Tool executed in the preceding chat turn.
- `last_response` (string/null, optional): Response returned in the preceding chat turn.

##### Example Request Body
```json
{
  "message": "Actually, change the doctor's name to Dr. Jane Doe.",
  "extracted_data": {
    "hcp_name": "Dr. Smith",
    "interaction_type": "Meeting",
    "date": "07/10/2026",
    "time": "14:00",
    "attendees": ["Nurse Jones"],
    "topics_discussed": ["Product X"],
    "materials_shared": [],
    "samples_distributed": [],
    "sentiment": "Positive",
    "outcomes": null,
    "follow_up_actions": []
  },
  "interaction_id": "8d026f0b-3e8f-4276-87bd-e48bb0f83d44",
  "last_intent": "LOG_INTERACTION",
  "last_tool": "log_interaction_tool",
  "last_response": "✅ Interaction logged successfully."
}
```

#### Response Schema (Pydantic model `ChatResponse`)
- `intent` (string): The classified intent of the user message.
- `selected_tool` (string/null): The tool executed during the graph run.
- `extracted_data` (object): The updated interaction form state dictionary.
- `response` (string): Conversational, context-aware AI text summary.
- `interaction_id` (string/null): UUID of the active logged interaction.
- `last_intent` (string/null): Active intent representing this turn.
- `last_tool` (string/null): Active tool representing this turn.
- `last_response` (string/null): Active response string representing this turn.

##### Example Response Body
```json
{
  "intent": "EDIT_INTERACTION",
  "selected_tool": "edit_interaction_tool",
  "extracted_data": {
    "hcp_name": "Dr. Jane Doe",
    "interaction_type": "Meeting",
    "date": "07/10/2026",
    "time": "14:00",
    "attendees": ["Nurse Jones"],
    "topics_discussed": ["Product X"],
    "materials_shared": [],
    "samples_distributed": [],
    "sentiment": "Positive",
    "outcomes": null,
    "follow_up_actions": []
  },
  "response": "I've successfully updated the doctor's name to Dr. Jane Doe. The meeting date, attendees, and topics discussed remain unchanged.",
  "interaction_id": "8d026f0b-3e8f-4276-87bd-e48bb0f83d44",
  "last_intent": "EDIT_INTERACTION",
  "last_tool": "edit_interaction_tool",
  "last_response": "✅ Interaction updated successfully."
}
```
