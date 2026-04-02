from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.gemini import GeminiSession, GeminiMessage
from models.user import User
from routes.auth import get_current_user
from services.gemini_service import generate_with_gemini
import os, shutil, uuid

router = APIRouter(prefix="/gemini", tags=["Gemini AI"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.post("/session")
def create_session(
    title: str = "New Session",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = GeminiSession(user_id=current_user.user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/session/{session_id}/chat")
async def chat(
    session_id: int,
    prompt: str,
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_path = None
    if file:
        ext = file.filename.split(".")[-1]
        filename = f"gemini_{uuid.uuid4()}.{ext}"
        image_path = os.path.join(UPLOAD_DIR, filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    response_text, output_image = await generate_with_gemini(prompt, image_path)

    message = GeminiMessage(
        session_id=session_id,
        role="user",
        prompt=prompt,
        response=response_text,
        image_input=image_path,
        image_output=output_image
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/session/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    return db.query(GeminiMessage).filter(GeminiMessage.session_id == session_id).all()
