from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.models.document import Document
from app.schemas.document_schema import DocumentResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
import shutil
import os
from fastapi import HTTPException
from app.utils.auth import role_required_with_cache

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_FOLDER = "documents"

@router.post("/", response_model=DocumentResponseSchema)
async def upload_document(
    mechanic_id: int = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(role_required_with_cache(["mechanic", "admin"]))
):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(mechanic_id=mechanic_id, type=type, file_path=file_path)
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

@router.put("/{document_id}", response_model=DocumentResponseSchema)
async def update_document(document_id: int, type: str = Form(...), file: UploadFile = File(None), db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["mechanic", "admin"]))):
    from sqlalchemy.future import select
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Документ не знайдено")
    if current_user.role != "admin" and document.mechanic_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")
    document.type = type
    if file:
        file_path = f"documents/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        document.file_path = file_path
    await db.commit()
    await db.refresh(document)
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["mechanic", "admin"]))):
    from sqlalchemy.future import select
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Документ не знайдено")
    if current_user.role != "admin" and document.mechanic_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу")
    await db.delete(document)
    await db.commit()
    return {"detail": "Документ видалено"}
