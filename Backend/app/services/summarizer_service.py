from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

def summarize_text(text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template = (
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

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        summary = chain.run(text=text)
        return summary
    except Exception as e:
        return f"Error generating summary: {e}"
    
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

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        enhanced_prompt = chain.run(prompt_text=prompt_text)
        return enhanced_prompt
    except Exception as e:
        return f"Error enhancing prompt: {e}"
