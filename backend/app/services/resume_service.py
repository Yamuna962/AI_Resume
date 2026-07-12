import uuid

from fastapi import UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.resume_repository import resume_repo
from app.schemas.resume import ResumeUploadResponse
from app.utils.pdf_extractor import extract_text_from_pdf_detailed


class ResumeService:
    async def upload_resume(self, db: AsyncSession, user_id: uuid.UUID, file: UploadFile) -> ResumeUploadResponse:
        content = await file.read()
        
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are supported")
            
        result = extract_text_from_pdf_detailed(content)

        logger.info(
            f"Resume uploaded: method={result.extraction_method} "
            f"quality={result.quality_score} chars={result.char_count}"
        )

        text = result.text

        if not text or len(text.strip()) < 80:
            raise ValueError(
                "Could not extract readable text from this PDF. "
                "Please upload a text-based PDF (export from Word/Google Docs, not a scanned image)."
            )
        
        # Here we would normally upload `content` to Supabase Storage
        # For simplicity in this scaffold, we'll store a mock URL
        storage_url = f"https://mock.supabase.co/storage/v1/object/public/resumes/{user_id}/{file.filename}"
        
        new_resume = await resume_repo.create(
            db,
            obj_in={
                "user_id": user_id,
                "filename": file.filename,
                "storage_url": storage_url,
                "raw_text": text,
                "file_size": len(content),
            }
        )
        
        return ResumeUploadResponse(
            resume_id=new_resume.id,
            filename=new_resume.filename,
            storage_url=new_resume.storage_url,
            file_size=new_resume.file_size,
            text_extracted=bool(new_resume.raw_text and new_resume.raw_text.strip()),
        )


resume_service = ResumeService()
