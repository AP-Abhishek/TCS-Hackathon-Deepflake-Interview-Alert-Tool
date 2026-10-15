"""
proctor/face_mesh.py
---------------------
Universal FaceMesh Provider:
Supports both legacy MediaPipe (mp.solutions.face_mesh) and modern
MediaPipe Tasks (mediapipe.tasks.python.vision.FaceLandmarker for MediaPipe >= 1.0 / Python 3.14).
Automatically downloads the official Google face_landmarker.task model if needed.
"""

import os
import urllib.request
from pathlib import Path
import numpy as np

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
MODEL_PATH = Path(__file__).resolve().parent.parent / "face_landmarker.task"


class LandmarkWrapper:
    def __init__(self, landmarks):
        self.landmark = landmarks

    def __getitem__(self, idx):
        return self.landmark[idx]

    def __len__(self):
        return len(self.landmark)


class FaceMeshResultWrapper:
    def __init__(self, face_landmarks):
        self.multi_face_landmarks = (
            [LandmarkWrapper(f) for f in face_landmarks] if face_landmarks else []
        )


class TasksFaceMeshAdapter:
    def __init__(self, max_num_faces: int = 2):
        if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size < 1000:
            print("[FaceMesh] Downloading official face_landmarker.task model bundle...")
            urllib.request.urlretrieve(MODEL_URL, str(MODEL_PATH))
            print(f"[FaceMesh] Model ready ({MODEL_PATH.stat().st_size} bytes).")

        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        self._mp = mp
        base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=max_num_faces,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def process(self, rgb_frame: np.ndarray):
        mp_image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB, data=rgb_frame
        )
        res = self.detector.detect(mp_image)
        return FaceMeshResultWrapper(res.face_landmarks)

    def close(self):
        if hasattr(self, "detector") and self.detector:
            self.detector.close()


def get_face_mesh(max_num_faces: int = 2):
    """
    Returns a FaceMesh instance compatible with results.multi_face_landmarks[0].landmark[idx].
    Automatically uses legacy mp.solutions.face_mesh if available, or the new Tasks API.
    """
    import mediapipe as mp

    if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
        return mp.solutions.face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
    return TasksFaceMeshAdapter(max_num_faces=max_num_faces)
