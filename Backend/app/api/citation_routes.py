from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.semantic_retrieval_service import unified_semantic_search

router = APIRouter(
    prefix="/citation_router",
    tags=["citation_router"],
)


class CitationRequest(BaseModel):
    text: str
    use_arxiv: Optional[bool] = True
    use_semantic_scholar: Optional[bool] = True
    max_results_per_source: Optional[int] = 5
    top_k: Optional[int] = 10
    use_sbert: Optional[bool] = True

class Paper(BaseModel):
    title: str
    authors: List[str]
    summary: str
    link: str
    published: str
    score: float  # similarity score
    source: Optional[str] = None
    venue: Optional[str] = None
    paperId: Optional[str] = None

class CitationResponse(BaseModel):
    query: str
    results: List[Paper]
    sources_used: List[str]


# -----------------------
# Semantic citation recommender with arXiv + Semantic Scholar
# -----------------------
@router.post("/recommend", response_model=CitationResponse)
async def recommend_citation(request: CitationRequest):
    """
    Recommend citations based on semantic similarity.
    Uses unified_semantic_search (same as semantic_routes) for efficient retrieval.
    Searches both arXiv and Semantic Scholar for relevant papers.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Use unified_semantic_search for efficient retrieval (same as semantic_routes)
        # This handles deduplication, parallel API calls, and semantic ranking automatically
        retrieved_papers = await unified_semantic_search(
            query=request.text,
            max_results_per_source=request.max_results_per_source,
            top_k=request.top_k,
            use_sbert=request.use_sbert,
            use_arxiv=request.use_arxiv,
            use_semantic_scholar=request.use_semantic_scholar
        )

        # Determine which sources were actually used
        sources_used = []
        if request.use_arxiv:
            sources_used.append("arXiv")
        if request.use_semantic_scholar:
            sources_used.append("Semantic Scholar")

        # Papers are already ranked by semantic similarity from unified_semantic_search
        # Ensure all papers have required fields (same validation as semantic_routes)
        for paper in retrieved_papers:
            if paper.get("summary") is None or not isinstance(paper.get("summary"), str):
                paper["summary"] = "No abstract available"
            if paper.get("title") is None:
                paper["title"] = "No title"
            if not isinstance(paper.get("authors"), list):
                paper["authors"] = []
            if "source" not in paper:
                paper["source"] = "unknown"

        return {
            "query": request.text,
            "results": retrieved_papers,
            "sources_used": sources_used
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recommending citations: {str(e)}")
