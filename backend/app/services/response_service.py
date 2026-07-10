from app.ai.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

logger = logging.getLogger(__name__)

RESPONSE_GENERATION_PROMPT = """You are a professional medical CRM conversational assistant.
Your task is to generate a natural, professional, and context-aware conversational response to the user based on the tool's execution result.

Context:
- User Input: {user_input}
- Detected Intent: {intent}
- Current Extracted Data: {extracted_data}
- Tool Execution Result: {tool_response}

Instructions:
1. Be professional, conversational, and concise. Avoid robotic or template-like phrasing.
2. Summarize only meaningful information. Do not invent missing values.
3. Omit fields that are null, empty, or not discussed.
4. Never repeat the raw JSON format in the response.
5. Never mention internal technical details (like database IDs, LangGraph, tool names, schemas, SQL, SQLite, or backend).
6. Provide a natural offer to help at the end when appropriate (e.g., "Let me know if you'd like to schedule a follow-up or add any other details.").
7. If the intent is HISTORY_SEARCH, summarize the matching records conversationalized into a clear, readable report instead of dumping list items.
8. If the intent is MATERIAL_RECOMMENDATION, list the recommended materials clearly and explain why they are relevant.
9. If the user's message is a simple greeting or acknowledgment, keep the response friendly, conversational, and helpful.

Generated Conversational Response:"""

def generate_ai_response(
    user_input: str,
    intent: str,
    extracted_data: dict,
    tool_response: str
) -> str:
    """
    Generates a professional natural language conversational reply from the CRM context using Groq LLM.
    """
    # If tool response is empty or a simple clarification question, return it directly
    if not tool_response:
        return ""
    if tool_response.endswith("?") and not tool_response.startswith("✅") and not tool_response.startswith("I found"):
        return tool_response

    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(RESPONSE_GENERATION_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({
            "user_input": user_input,
            "intent": intent,
            "extracted_data": json.dumps(extracted_data),
            "tool_response": tool_response
        })
        return response.content.strip()
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        # Fallback to the robotic/tool response on failure
        return tool_response
