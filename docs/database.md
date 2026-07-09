# Database Documentation

This document describes the database design, schema tables, indexes, and migration strategies for the PostgreSQL database.

---

## Database ER Overview
The application maintains a single, stateful table named `interactions` that stores HCP meeting log entities.

---

## Schema definition (interactions Table)

```mermaid
erDiagram
    interactions {
        varchar(36) id PK "UUID Primary Key"
        varchar(255) hcp_name "Name of the HCP"
        varchar(50) interaction_type "Meeting, Call, Email, etc."
        varchar(100) date "Interaction Date string"
        varchar(50) time "Interaction Time string"
        json attendees "Attendees list JSON array"
        json topics_discussed "Discussed topics JSON array"
        json materials_shared "Attached materials JSON array"
        json samples_distributed "Distributed samples JSON array"
        varchar(50) sentiment "HCP Sentiment"
        text outcomes "Interaction outcome details"
        json follow_up_actions "Scheduled follow-up actions JSON array"
        timestamp_with_timezone created_at "Created timestamp in UTC"
        timestamp_with_timezone updated_at "Last updated timestamp in UTC"
    }
```

---

## Field Descriptions

| Column | Data Type | Constraint | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`id`** | `VARCHAR(36)` | `PRIMARY KEY` | *UUID String* | Unique ID for the interaction log record. |
| **`hcp_name`** | `VARCHAR(255)` | `NULL` | `None` | Name of the target healthcare provider (HCP). |
| **`interaction_type`** | `VARCHAR(50)` | `NULL` | `"Meeting"` | Format of interaction. |
| **`date`** | `VARCHAR(100)` | `NULL` | `None` | Structured date (e.g. `07/10/2026`). |
| **`time`** | `VARCHAR(50)` | `NULL` | `None` | Structured time (e.g. `14:00`). |
| **`attendees`** | `JSON` | `NOT NULL` | `[]` | JSON array containing strings of attendees. |
| **`topics_discussed`** | `JSON` | `NOT NULL` | `[]` | JSON array containing strings of clinical topics discussed. |
| **`materials_shared`** | `JSON` | `NOT NULL` | `[]` | JSON array containing strings of shared brochure materials. |
| **`samples_distributed`**| `JSON` | `NOT NULL` | `[]` | JSON array containing strings of distributed product samples. |
| **`sentiment`** | `VARCHAR(50)` | `NULL` | `None` | HCP Sentiment (Positive, Neutral, Negative). |
| **`outcomes`** | `TEXT` | `NULL` | `None` | Text description containing clinical outcomes or meeting notes. |
| **`follow_up_actions`** | `JSON` | `NOT NULL` | `[]` | JSON array containing follow-up scheduling strings. |
| **`created_at`** | `TIMESTAMP WITH TZ` | `NOT NULL` | *UTC Now* | Database insertion timestamp. |
| **`updated_at`** | `TIMESTAMP WITH TZ` | `NOT NULL` | *UTC Now* | Last modification timestamp. |

---

## Migration Strategy

### Alembic Migrations
- Migration files are stored inside [backend/alembic/versions/](file:///c:/Users/LENOVO/Downloads/hcp-ai-crm/backend/alembic/versions/).
- Connection URLs are loaded dynamically from environment variables, eliminating hardcoded passwords in version control.
- Executing migrations:
  ```bash
  alembic upgrade head
  ```
