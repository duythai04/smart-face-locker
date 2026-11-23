import numpy as np

from threading import Lock
from insightface.app import FaceAnalysis


class FaceRecognizer:
    """
    Face Recognition sử dụng:
    - SCRFD: Face Detection
    - ArcFace: Face Embedding
    """

    def __init__(self):

        print("[AI] Loading Face Recognition model...")

        self.model = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            allowed_modules=[
                "detection",
                "recognition"
            ]
        )

        self.model.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

        print("[AI] Face Recognition model ready!")

    def extract_embedding(self, image: np.ndarray):
        """
        Trích xuất embedding từ ảnh.

        Yêu cầu ảnh có đúng một khuôn mặt.
        """

        faces = self.model.get(image)

        if len(faces) == 0:
            raise ValueError(
                "NO_FACE_DETECTED"
            )

        if len(faces) > 1:
            raise ValueError(
                "MULTIPLE_FACES_DETECTED"
            )

        face = faces[0]

        embedding = face.embedding

        if embedding is None:
            raise ValueError(
                "EMBEDDING_FAILED"
            )

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        )

        norm = np.linalg.norm(embedding)

        if not np.isfinite(norm) or norm <= 1e-12:
            raise ValueError(
                "INVALID_EMBEDDING"
            )

        normalized_embedding = embedding / norm

        if not np.all(np.isfinite(normalized_embedding)):
            raise ValueError(
                "INVALID_EMBEDDING"
            )

        return {
            "embedding": normalized_embedding,
            "bbox": face.bbox.astype(int).tolist(),
            "confidence": float(face.det_score)
        }

    @staticmethod
    def cosine_similarity(
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ):
        """
        Tính cosine similarity giữa hai embedding.
        """

        embedding1 = np.asarray(
            embedding1,
            dtype=np.float32
        )

        embedding2 = np.asarray(
            embedding2,
            dtype=np.float32
        )

        if embedding1.shape != embedding2.shape:
            raise ValueError(
                "EMBEDDING_DIMENSION_MISMATCH"
            )

        if embedding1.ndim != 1:
            raise ValueError(
                "INVALID_EMBEDDING_SHAPE"
            )

        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 <= 1e-12 or norm2 <= 1e-12:
            raise ValueError(
                "INVALID_EMBEDDING"
            )

        similarity = np.dot(
            embedding1,
            embedding2
        ) / (norm1 * norm2)

        return float(
            np.clip(similarity, -1.0, 1.0)
        )

    def verify(
        self,
        image1: np.ndarray,
        image2: np.ndarray,
        threshold: float = 0.45
    ):
        """
        So sánh hai khuôn mặt.

        threshold=0.45 chỉ là giá trị thử nghiệm,
        chưa được hiệu chuẩn cho hệ thống thực tế.
        """

        result1 = self.extract_embedding(image1)
        result2 = self.extract_embedding(image2)

        similarity = self.cosine_similarity(
            result1["embedding"],
            result2["embedding"]
        )

        return {
            "is_match": bool(similarity >= threshold),
            "similarity": similarity,
            "threshold": threshold,
            "face1": {
                "bbox": result1["bbox"],
                "confidence": result1["confidence"]
            },
            "face2": {
                "bbox": result2["bbox"],
                "confidence": result2["confidence"]
            }
        }


_face_recognizer = None
_recognizer_lock = Lock()


def get_face_recognizer():
    """
    Chỉ khởi tạo model một lần trong mỗi tiến trình.
    """

    global _face_recognizer

    if _face_recognizer is None:

        with _recognizer_lock:

            if _face_recognizer is None:
                _face_recognizer = FaceRecognizer()

    return _face_recognizer