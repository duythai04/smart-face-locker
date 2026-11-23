import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from app.ai.face_detector import get_face_detector
from app.ai.face_recognizer import get_face_recognizer


router = APIRouter(
    prefix="/api/face",
    tags=["Face Recognition"]
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000

# Chỉ dùng để thử nghiệm
DEMO_THRESHOLD = 0.45


async def read_image(file: UploadFile):
    """
    Đọc và kiểm tra ảnh upload.
    """

    if file.content_type not in [
        "image/jpeg",
        "image/png"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )

    image_bytes = await file.read(
        MAX_IMAGE_SIZE + 1
    )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image is too large"
        )

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty image"
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

    if width * height > MAX_IMAGE_PIXELS:
        raise HTTPException(
            status_code=413,
            detail="Image resolution is too large"
        )

    return image


def handle_ai_error(error: ValueError):
    """
    Chuyển lỗi AI thành HTTP response.
    """

    error_code = str(error)

    if error_code == "NO_FACE_DETECTED":
        raise HTTPException(
            status_code=422,
            detail="No face detected"
        )

    if error_code == "MULTIPLE_FACES_DETECTED":
        raise HTTPException(
            status_code=422,
            detail="Multiple faces detected"
        )

    raise HTTPException(
        status_code=422,
        detail="Face processing failed"
    )


@router.post("/detect")
async def detect_face(
    file: UploadFile = File(...)
):
    """
    Phát hiện khuôn mặt bằng SCRFD.
    """

    image = await read_image(file)

    detector = get_face_detector()

    faces = detector.detect(image)

    return {
        "success": True,
        "face_count": len(faces),
        "faces": faces
    }


@router.post("/embed")
async def extract_face_embedding(
    file: UploadFile = File(...)
):
    """
    Trích xuất embedding bằng ArcFace.

    Chỉ sử dụng trong môi trường phát triển.
    """

    image = await read_image(file)

    recognizer = get_face_recognizer()

    try:
        result = recognizer.extract_embedding(image)

    except ValueError as error:
        handle_ai_error(error)

    embedding = result["embedding"]

    return {
        "success": True,
        "embedding_dimension": int(embedding.shape[0]),
        "embedding": embedding.tolist(),
        "face": {
            "bbox": result["bbox"],
            "confidence": result["confidence"]
        }
    }


@router.post("/verify")
async def verify_faces(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """
    So sánh hai ảnh khuôn mặt.

    API thử nghiệm, chưa cấp quyền mở tủ.
    """

    image1 = await read_image(file1)
    image2 = await read_image(file2)

    recognizer = get_face_recognizer()

    try:
        result = recognizer.verify(
            image1=image1,
            image2=image2,
            threshold=DEMO_THRESHOLD
        )

    except ValueError as error:
        handle_ai_error(error)

    return {
        "success": True,
        "is_match": result["is_match"],
        "similarity": result["similarity"],
        "threshold": result["threshold"],
        "face1": result["face1"],
        "face2": result["face2"]
    }