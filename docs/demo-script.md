# Live Demo Script

This script outlines a 5–7 minute walkthrough demonstrating the core functionalities of the HCP AI CRM Assistant.

---

## Part 1: Introduction (1 Minute)

### Script
> "Hello everyone. Today, I am demonstrating the **HCP AI CRM Assistant**—an enterprise-grade solution designed to eliminate administrative overhead for medical representatives. Instead of manually filling out tedious database forms, representatives can simply dictate or chat with our AI assistant to log meetings, search interaction histories, attach recommended educational materials, and schedule follow-ups.
>
> On the frontend, we have a responsive split-screen: the left side displays the read-only interaction form, and the right side features our conversational assistant. Our backend runs on FastAPI, PostgreSQL, and LangGraph."

---

## Part 2: Feature Demos (4 Minutes)

### Scenario A: Log an Interaction
1. **Action**: Click the microphone icon in the chat box, wait for it to pulse, and speak clearly:
   > *"Met Dr. Smith today at 2:00 PM. We discussed Product X efficacy. He was very positive about the clinical trial results. I also distributed 5 samples."*
   *(Alternatively, type the text in the input box and click Send.)*
2. **Observe**:
   - The microphone pulses red during recording and auto-submits on silence.
   - The AI responds with a natural conversational message summarizing the logged details.
   - The left-hand form updates dynamically. Fields like **HCP Name** (Dr. Smith), **Date**, **Time**, **Topics**, and **Samples** animate with a subtle blue highlight glow indicating state synchronization.
   - **Sentiment** displays a green **Positive** badge.

### Scenario B: Context-Aware Editing (Conversation Memory)
1. **Action**: In the chat box, type and send:
   > *"Actually, change the doctor's name to Dr. John Smith and set the time to 3:00 PM."*
2. **Observe**:
   - The AI identifies the context from the active interaction ID and modifies only the targeted fields.
   - The left-hand form updates: the HCP Name field updates to "Dr. John Smith", and the time changes to "3:00 PM", highlighting the edited cells.

### Scenario C: Schedule a Follow-Up
1. **Action**: Type and send:
   > *"Schedule a follow up call next Monday."*
2. **Observe**:
   - The AI schedules the action.
   - The **Follow-up Actions** section on the left-hand form displays a new tag: `"Next Monday"`.

### Scenario D: Natural Language History Search
1. **Action**: Type and send:
   > *"Show my meetings with Dr. John Smith"*
2. **Observe**:
   - The AI classifies this as a history search request.
   - It queries the database, extracts matches, and returns a formatted list of past interactions with Dr. John Smith directly in the chat panel.

---

## Part 3: Database Verification (1 Minute)

### Script
> "Every action taken during this session is backed by a transactional PostgreSQL database. To verify that our conversational changes were committed, we can inspect our PostgreSQL server."

1. **Action**: Open pgAdmin 4 or query the database:
   ```sql
   SELECT id, hcp_name, sentiment, follow_up_actions 
   FROM public.interactions 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```
2. **Observe**: The output row matches the logged details exactly:
   - `hcp_name`: Dr. John Smith
   - `sentiment`: Positive
   - `follow_up_actions`: `["Next Monday"]`

---

## Part 4: Conclusion (30 Seconds)

### Script
> "As demonstrated, the assistant seamlessly processes speech-to-text inputs, updates database models, and generates natural language responses, providing medical representatives with an intuitive and efficient CRM experience. Thank you!"
