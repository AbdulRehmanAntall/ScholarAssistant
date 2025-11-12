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
# 1️⃣ Summarize Text
# ---------------------------
def summarize_text(text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are an expert academic researcher tasked with summarizing complex scholarly material.\n"
            "Read the following academic text carefully and produce a structured, professional summary that:\n"
            "- Captures the central argument, objectives, and key findings clearly.\n"
            "- Preserves important technical terms, data, and context.\n"
            "- Avoids unnecessary repetition or opinion.\n"
            "- Uses formal academic tone and concise phrasing.\n"
            "- Maintains coherence and logical flow.\n\n"
            "Academic Text:\n{text}\n\n"
            "Research Summary:"
        ),
    )

    chain = prompt | llm | parser
    try:
        return chain.invoke({"text": text})
    except Exception as e:
        return f"Error generating summary: {e}"


# ---------------------------
# 2️⃣ Summarize PDF
# ---------------------------
def summarize_pdf(text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are an expert academic researcher.\n"
            "Summarize the following PDF text clearly, capturing objectives, methods, results, "
            "key findings, and conclusions.\n"
            "Preserve technical terms and maintain formal academic tone.\n\n"
            "PDF Text:\n{text}\n\nSummary:"
        ),
    )
    chain = prompt | llm | parser
    return chain.invoke({"text": text})


# ---------------------------
# 3️⃣ Enhance Prompt
# ---------------------------
def enhance_prompt(prompt_text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["prompt_text"],
        template=(
            "You are an expert prompt engineer and language coach.\n"
            "Your job is to take the user's question or prompt and rewrite it so that it:\n"
            "- Fixes grammatical or language issues\n"
            "- Improves clarity and structure\n"
            "- Adds instructions for better AI responses (e.g., 'explain step by step', 'give examples', etc.)\n"
            "- Makes it specific, engaging, and suitable for use with an AI model.\n\n"
            "Example:\n"
            "User Prompt: What is machine learning?\n"
            "Enhanced Prompt: Explain the concept of machine learning in simple terms. "
            "Provide real-world examples, mention key algorithms, and explain how it differs from traditional programming.\n\n"
            "Now, enhance the following prompt:\n\n"
            "User Prompt: {prompt_text}\n\n"
            "Enhanced Prompt:"
        ),
    )

    chain = prompt | llm | parser
    try:
        return chain.invoke({"prompt_text": prompt_text})
    except Exception as e:
        return f"Error enhancing prompt: {e}"


# ---------------------------
# 4️⃣ Answer Question (Multi-PDF)
# ---------------------------
def answer_question(pdf_texts: list, question: str, conversation_history: str) -> str:
    combined_texts = ""
    for i, text in enumerate(pdf_texts, 1):
        combined_texts += f"[PDF {i}]\n{text}\n\n"

    print(combined_texts)
    prompt = PromptTemplate(
        input_variables=["pdfs", "question", "history"],
        template=(
            "You are an expert academic assistant.\n"
            "Use the following PDFs and previous conversation to answer the user's question.\n\n"
            "PDFs:\n{pdfs}\n\n"
            "Conversation History:\n{history}\n\n"
            "User Question:\n{question}\n\n"
            "Answer in a clear, structured, academic tone. Include bullet points for technical/methodology steps. "
            "Cite PDF numbers when referencing content."
        ),
    )

    chain = prompt | llm | parser
    return chain.invoke({
        "pdfs": combined_texts,
        "question": question,
        "history": conversation_history
    })

async def generate_search_query(text: str) -> list[str]:
    """
    Generate multiple concise search keywords/queries from user-provided text
    using PromptTemplate -> LLM -> parser pattern.
    Returns a list of search queries.
    """
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are an academic research assistant.\n"
            "Given the following paragraph, generate 3-5 concise search queries "
            "focusing on technical keywords, concepts, and relevant terminology. "
            "Return them as a comma-separated list.\n\n"
            "Paragraph:\n{text}\n\n"
            "Output only a comma-separated list of concise queries suitable for scholarly search."
        )
    )

    chain = prompt | llm | parser

    try:
        # Get the raw comma-separated string
        result = chain.invoke({"text": text})
        # Split by comma and clean whitespace
        queries = [q.strip() for q in result.split(",") if q.strip()]
        return queries
    except Exception as e:
        print(f"Error generating search queries: {e}")
        return []
