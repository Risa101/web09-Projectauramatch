from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.gemini import GeminiSession, GeminiMessage
from models.analysis import AnalysisResult
from models.user import User
from routes.auth import get_current_user
from services.rag_service import generate_rag_response
import os, shutil, uuid

router = APIRouter(prefix="/gemini", tags=["Gemini AI"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.post("/session")
def create_session(
    title: str = "New Session",
    analysis_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Auto-attach latest analysis if none specified
    if analysis_id is None:
        latest = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.user_id == current_user.user_id)
            .order_by(AnalysisResult.created_at.desc())
            .first()
        )
        if latest:
            analysis_id = latest.analysis_id

    session = GeminiSession(
        user_id=current_user.user_id,
        analysis_id=analysis_id,
        title=title,
    )
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
    # Verify session belongs to user
    session = (
        db.query(GeminiSession)
        .filter(
            GeminiSession.session_id == session_id,
            GeminiSession.user_id == current_user.user_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Handle image upload
    image_path = None
    if file:
        ext = file.filename.split(".")[-1]
        filename = f"gemini_{uuid.uuid4()}.{ext}"
        image_path = os.path.join(UPLOAD_DIR, filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    # Load chat history
    previous_messages = (
        db.query(GeminiMessage)
        .filter(GeminiMessage.session_id == session_id)
        .order_by(GeminiMessage.created_at.asc())
        .all()
    )

    # Load analysis if linked
    analysis = None
    if session.analysis_id:
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.analysis_id == session.analysis_id)
            .first()
        )

    # RAG-augmented generation
    response_text, output_image = await generate_rag_response(
        prompt=prompt,
        session_messages=previous_messages,
        analysis=analysis,
        image_path=image_path,
        db=db,
    )

    message = GeminiMessage(
        session_id=session_id,
        role="user",
        prompt=prompt,
        response=response_text,
        image_input=image_path,
        image_output=output_image,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/session/{session_id}/messages")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    return (
        db.query(GeminiMessage)
        .filter(GeminiMessage.session_id == session_id)
        .order_by(GeminiMessage.created_at.asc())
        .all()
    )
