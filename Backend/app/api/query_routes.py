from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional


router = APIRouter(
    prefix="/queries",
    tags=["queries"],
)


@router.get("/")
async def return_query_api_status():
    return {"status": "Query API is running"}