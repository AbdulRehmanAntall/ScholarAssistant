from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional


router = APIRouter(
    prefix="/pdfs",
    tags=["pdfs"],
)


@router.get("/")
async def return_pdf_api_status():
    return {"status": "PDF API is running"}