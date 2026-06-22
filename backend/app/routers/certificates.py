import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.services import cert_gen

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("", response_model=schemas.CertificateOut)
async def get_certificate(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the generated certificate details for the current user.
    """
    query = select(models.Certificate).where(models.Certificate.user_id == current_user.user_id)
    result = await db.execute(query)
    certificate = result.scalars().first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not yet generated for this user."
        )
        
    return schemas.CertificateOut(
        certificate_id=certificate.certificate_id,
        certificate_code=certificate.certificate_code,
        issue_date=certificate.issue_date,
        name=current_user.name,
        course_name="AI Data Science Course"
    )


@router.post("/generate", response_model=schemas.CertificateOut)
async def generate_certificate(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates final progress. If all 12 lessons are completed,
    registers a new certificate.
    """
    user_id = current_user.user_id
    
    # 1. Verify all 12 lessons are completed
    total_lessons_query = select(func.count(models.Lesson.lesson_id))
    total_lessons_res = await db.execute(total_lessons_query)
    total_lessons = total_lessons_res.scalar() or 12
    
    completed_query = select(func.count(models.Progress.progress_id)).where(
        models.Progress.user_id == user_id,
        models.Progress.status == "completed"
    )
    completed_res = await db.execute(completed_query)
    completed_count = completed_res.scalar() or 0
    
    if completed_count < total_lessons:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Course incomplete. You have completed {completed_count}/{total_lessons} lessons."
        )
        
    # 2. Check if already generated
    existing_query = select(models.Certificate).where(models.Certificate.user_id == user_id)
    existing_res = await db.execute(existing_query)
    certificate = existing_res.scalars().first()
    
    if not certificate:
        # Generate new unique certificate code
        rand_code = f"DS-{datetime.utcnow().year}-{random.randint(100000, 999999)}"
        certificate = models.Certificate(
            user_id=user_id,
            certificate_code=rand_code,
            issue_date=datetime.utcnow()
        )
        db.add(certificate)
        await db.commit()
        await db.refresh(certificate)
        
    return schemas.CertificateOut(
        certificate_id=certificate.certificate_id,
        certificate_code=certificate.certificate_code,
        issue_date=certificate.issue_date,
        name=current_user.name,
        course_name="AI Data Science Course"
    )


@router.get("/download")
async def download_certificate(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Streams the generated certificate as a PDF download.
    """
    # Fetch certificate details
    query = select(models.Certificate).where(models.Certificate.user_id == current_user.user_id)
    result = await db.execute(query)
    certificate = result.scalars().first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No certificate record found. Please generate it first."
        )
        
    # Generate the PDF byte stream
    pdf_buffer = cert_gen.generate_pdf_certificate(
        student_name=current_user.name,
        issue_date=certificate.issue_date,
        cert_code=certificate.certificate_code
    )
    
    # Return streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Certificate_{current_user.name.replace(' ', '_')}.pdf"
        }
    )
