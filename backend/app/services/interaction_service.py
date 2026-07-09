from app.ai.llm import get_llm
from app.schemas.interaction import InteractionExtraction
from langchain_core.prompts import ChatPromptTemplate

EXTRACTION_PROMPT = """You are an expert clinical data extraction assistant.
Extract structured details from the following description of a Healthcare Professional (HCP) interaction.
Fill in every field based on the input text. If a field is not mentioned in the text, leave it as null (None) or an empty list.

Input text:
{user_input}
"""

def extract_interaction_details(user_input: str) -> InteractionExtraction:
    """Accepts unstructured user input and returns structured InteractionExtraction data using Groq LLM."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(InteractionExtraction)
    
    prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)
    chain = prompt | structured_llm
    
    # Execute extraction
    result = chain.invoke({"user_input": user_input})
    return result
