import cv2
import numpy as np

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.ai.face_detector import get_face_detector


router = APIRouter(
    prefix="/api/face",
    tags=["Face Recognition"]
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024


@router.post("/detect")
async def detect_face(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )

    image_bytes = await file.read(MAX_IMAGE_SIZE + 1)

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image is too large"
        )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image"
        )

    height, width = image.shape[:2]

    if width * height > 12_000_000:
        raise HTTPException(
            status_code=413,
            detail="Image resolution is too large"
        )

    faces = get_face_detector().detect(image)

    return {
        "success": True,
        "face_count": len(faces),
        "faces": faces
    }