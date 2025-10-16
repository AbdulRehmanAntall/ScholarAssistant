from fastapi import APIRouter,Depends,Path,HTTPException,Query,UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional
from app.utils.pdf_parser import extract_text_and_formulas
from app.utils.text_cleanup import clean_extracted_text

from PyPDF2 import PdfReader

router = APIRouter(
    prefix="/pdfs",
    tags=["pdfs"],
)


@router.get("/")
async def return_pdf_api_status():
    return {"status": "PDF API is running"}


@router.post("/extract")
async def extract_text_and_math(file: UploadFile = File(...)):
    """
    Upload a PDF or DOCX file and extract both text and mathematical formulas.
    """
    try:
        file_bytes = await file.read()
        result = extract_text_and_formulas(file.filename, file_bytes)
        if result["text"]:
            result["text"] = clean_extracted_text(result["text"])

        return {
            "filename": file.filename,
            "text": result["text"],
            "formulas": result["formulas"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")