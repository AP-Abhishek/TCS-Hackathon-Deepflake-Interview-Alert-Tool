"""Candidate face-presence and multi-person tracking."""

from numbers import Integral


class PresenceTracker:
    """Convert a face detector's count into the shared presence data contract."""

    def update(self, face_count: int) -> dict:
        if isinstance(face_count, bool) or not isinstance(face_count, Integral):
            raise TypeError("face_count must be a non-negative integer")
        if face_count < 0:
            raise ValueError("face_count must be a non-negative integer")

        count = int(face_count)
        return {
            "face_count": count,
            "is_missing": count == 0,
            "is_multiple": count > 1,
        }
