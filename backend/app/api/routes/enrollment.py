import cv2
import numpy as np

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ai.face_recognizer import get_face_recognizer

from app.services.enrollment_service import (
    EnrollmentService,
    NoAvailableLockerError,
)


router = APIRouter(
    prefix="/api/locker-sessions",
    tags=["Locker Sessions"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/enroll")
async def enroll_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # Kiểm tra loại file.
    if file.content_type not in [
        "image/jpeg",
        "image/png",
    ]:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG and PNG images are supported",
        )

    contents = await file.read(MAX_FILE_SIZE + 1)

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image is too large",
        )

    # Chuyển bytes thành ảnh OpenCV.
    image_array = np.frombuffer(
        contents,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image",
        )

    height, width = image.shape[:2]

    if height * width > 12_000_000:
        raise HTTPException(
            status_code=413,
            detail="Image resolution is too large",
        )

    # Trích xuất embedding.
    try:
        recognizer = get_face_recognizer()

        result = recognizer.extract_embedding(image)

        embedding = result["embedding"].tolist()

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    # Cấp tủ và tạo phiên gửi đồ.
    try:
        enrollment = EnrollmentService.enroll(
            db=db,
            embedding=embedding,
        )

    except NoAvailableLockerError:
        raise HTTPException(
            status_code=409,
            detail="No available locker",
        )

    return {
        "success": True,
        "message": "Face enrolled successfully",
        **enrollment,
    }