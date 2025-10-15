from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional


router = APIRouter(
    prefix="/citations",
    tags=["citations"],
)


@router.get("/")
async def return_citattion_api_status():
    return {"status": "Citation API is running"}