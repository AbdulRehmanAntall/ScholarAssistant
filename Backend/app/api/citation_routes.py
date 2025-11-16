from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import arxiv
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.summarizer_service import generate_search_query
from app.services.arxiv_service import search_arxiv

router = APIRouter(
    prefix="/citation_router",
    tags=["citation_router"],
)


class CitationRequest(BaseModel):
    text: str

class Paper(BaseModel):
    title: str
    authors: List[str]
    summary: str
    link: str
    published: str
    score: float #this is the similarity score

class CitationResponse(BaseModel):
    query: str
    results: List[Paper]


async def get_embedding(text: str, model: str = "text-embedding-3-large") -> list[float]:
    """
    Generate vector embedding for text using OpenAI >=1.0 API
    Works asynchronously with await.
    """
    resp = openai.embeddings.create(
        model=model,
        input=text
    )
    return resp.data[0].embedding

# -----------------------
# Semantic citation recommender
# -----------------------
@router.post("/recommend", response_model=CitationResponse)
async def recommend_citation(request: CitationRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    user_text = request.text
    print("Received text:", user_text)

    # Generating high-quality search queries from text then to find relevant papers
    queries = await generate_search_query(user_text)
    print("Generated queries:", queries)

    # convwert user text to embedding
    user_embedding = await get_embedding(user_text)

    # fetching candidate papers from arxiv for each query
    candidate_papers = []
    for query in queries:
        papers = await search_arxiv(query, max_results=5)
        candidate_papers.extend(papers)

    # Computing embeddings for paper abstracts and semantic similarity
    for paper in candidate_papers:
        paper_embedding = await get_embedding(paper["summary"])
        score = cosine_similarity(
            np.array(user_embedding).reshape(1, -1),
            np.array(paper_embedding).reshape(1, -1)
        )[0][0]
        paper["score"] = float(score)

    # Remove duplicates
    unique_papers = {p['link']: p for p in candidate_papers}.values()

    # Ranking papers by similarity score
    ranked_papers = sorted(unique_papers, key=lambda x: x["score"], reverse=True)

    return {
        "query": ", ".join(queries),
        "results": ranked_papers[:10]  
    }
