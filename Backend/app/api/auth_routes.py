from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional

<<<<<<< HEAD
=======

>>>>>>> 67c81f5988411e19545807910e958b22cd513c65
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/")
async def return_auth_api_status():
    return {"status": "AUTH API is running"}