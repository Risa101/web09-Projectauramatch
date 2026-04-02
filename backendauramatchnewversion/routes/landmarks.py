from fastapi import APIRouter, UploadFile, File, HTTPException
from services.landmark_service import detect_landmarks
import os, shutil, uuid

router = APIRouter(prefix="/landmarks", tags=["Landmarks"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/detect")
async def detect_face_landmarks(file: UploadFile = File(...)):
    """รับรูปภาพแล้วส่ง 68 จุด landmark กลับ"""
    ext = file.filename.split(".")[-1]
    filename = f"landmark_{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = detect_landmarks(filepath)
    finally:
        # ลบไฟล์ชั่วคราว
        if os.path.exists(filepath):
            os.remove(filepath)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
