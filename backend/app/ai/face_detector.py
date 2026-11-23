import numpy as np

from insightface.app import FaceAnalysis


class FaceDetector:

    def __init__(self):

        self.model = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            allowed_modules=["detection"]
        )

        self.model.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

    def detect(self, image: np.ndarray):

        faces = self.model.get(image)

        results = []

        for face in faces:

            results.append({
                "bbox": face.bbox.astype(int).tolist(),
                "confidence": float(face.det_score)
            })

        return results


face_detector = None


def get_face_detector():

    global face_detector

    if face_detector is None:
        face_detector = FaceDetector()

    return face_detector