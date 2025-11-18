from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Shared model instance
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
parser = StrOutputParser()

# ---------------------------
# 0️⃣ Utility: Detect user instructions
# ---------------------------
def detect_user_instructions(prompt: str) -> dict:
    """
    Detects if user wants short/long, bullet points, step-by-step, examples, etc.
    Returns a dict of preferences.
    """
    instructions = {
        "concise": False,
        "detailed": False,
        "bullet_points": False,
        "step_by_step": False,
        "examples": False
    }

    lower = prompt.lower()
    if "short" in lower or "concise" in lower or "brief" in lower:
        instructions["concise"] = True
    if "long" in lower or "detailed" in lower or "elaborate" in lower:
        instructions["detailed"] = True
    if "bullet" in lower or "points" in lower:
        instructions["bullet_points"] = True
    if "step" in lower or "step by step" in lower:
        instructions["step_by_step"] = True
    if "example" in lower or "examples" in lower:
        instructions["examples"] = True

    return instructions

# ---------------------------
# 1️⃣ Adaptive prompt builder
# ---------------------------
def adaptive_prompt(user_prompt: str, base_instruction: str = "") -> str:
    """
    Build prompt dynamically based on detected user instructions.
    """
    instructions = detect_user_instructions(user_prompt)
    
    extra = []
    if instructions["concise"]:
        extra.append("Provide a brief, to-the-point answer.")
    if instructions["detailed"]:
        extra.append("Explain in detail with structured paragraphs.")
    if instructions["bullet_points"]:
        extra.append("Use bullet points for clarity.")
    if instructions["step_by_step"]:
        extra.append("Explain step by step.")
    if instructions["examples"]:
        extra.append("Provide examples where appropriate.")
    
    filled_prompt = (
        f"You are an expert academic assistant.\n"
        f"{base_instruction}\n"
        f"{' '.join(extra) if extra else 'Answer in a clear, standard style.'}\n\n"
        f"User Prompt: {user_prompt}\nAnswer:"
    )
    return filled_prompt

# ---------------------------
# 2️⃣ Summarize Text
# ---------------------------
def summarize_text(text: str) -> str:
    prompt_text = adaptive_prompt(
        text,
        base_instruction=(
            "Summarize complex scholarly material clearly, capturing objectives, "
            "key findings, technical terms, and logical flow. Avoid repetition or personal opinion."
        )
    )
    prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = prompt | llm | parser
    try:
        return chain.invoke({"prompt": prompt_text})
    except Exception as e:
        return f"Error generating summary: {e}"

# ---------------------------
# 3️⃣ Summarize PDF
# ---------------------------
def summarize_pdf(text: str) -> str:
    prompt_text = adaptive_prompt(
        text,
        base_instruction=(
            "Summarize the PDF content capturing objectives, methods, results, "
            "key findings, and conclusions. Preserve technical terms and maintain formal tone."
        )
    )
    prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = prompt | llm | parser
    try:
        return chain.invoke({"prompt": prompt_text})
    except Exception as e:
        return f"Error summarizing PDF: {e}"

# ---------------------------
# 4️⃣ Enhance Prompt
# ---------------------------
def enhance_prompt(prompt_text: str) -> str:
    prompt_text = adaptive_prompt(
        prompt_text,
        base_instruction=(
            "Rewrite the user's prompt for clarity, structure, and specificity. "
            "Add instructions for better AI responses if missing."
        )
    )
    prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = prompt | llm | parser
    try:
        return chain.invoke({"prompt": prompt_text})
    except Exception as e:
        return f"Error enhancing prompt: {e}"

# ---------------------------
# 5️⃣ Answer Question (Multi-PDF)
# ---------------------------
def answer_question(pdf_texts: list, question: str, conversation_history: str) -> str:
    combined_texts = ""
    for i, text in enumerate(pdf_texts, 1):
        combined_texts += f"[PDF {i}]\n{text}\n\n"
    
    base_instruction = (
        "Use the following PDFs and conversation history to answer the user's question. "
        "Include bullet points for methodology or technical steps and cite PDF numbers where relevant."
    )
    prompt_text = adaptive_prompt(question, base_instruction=base_instruction)
    
    prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = prompt | llm | parser
    try:
        return chain.invoke({"prompt": prompt_text})
    except Exception as e:
        return f"Error answering question: {e}"

# ---------------------------
# 6️⃣ Generate Search Queries
# ---------------------------
async def generate_search_query(text: str) -> list[str]:
    """
    Generate multiple concise search keywords/queries from user-provided text.
    """
    base_instruction = (
        "Generate 3-5 concise search queries focusing on technical keywords, concepts, "
        "and relevant terminology. Return as a comma-separated list."
    )
    prompt_text = adaptive_prompt(text, base_instruction=base_instruction)
    
    prompt = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = prompt | llm | parser
    try:
        result = chain.invoke({"prompt": prompt_text})
        queries = [q.strip() for q in result.split(",") if q.strip()]
        return queries
    except Exception as e:
        print(f"Error generating search queries: {e}")
        return []
