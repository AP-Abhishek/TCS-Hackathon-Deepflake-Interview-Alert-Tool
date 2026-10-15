"""Eye-gaze direction and off-screen duration tracking."""

from math import isfinite
from time import monotonic
from typing import Optional, Sequence


class GazeTracker:
    """Estimate horizontal gaze direction from MediaPipe Face Mesh landmarks."""

    LEFT_IRIS = 468
    RIGHT_IRIS = 473
    EYE_CORNERS = ((33, 133, LEFT_IRIS), (362, 263, RIGHT_IRIS))

    def __init__(self, away_threshold: float = 2.5):
        if not isfinite(away_threshold) or away_threshold < 0:
            raise ValueError("away_threshold must be a finite, non-negative number")
        self.away_threshold = away_threshold
        self._away_since: Optional[float] = None

    def update(self, landmarks: Optional[Sequence], now: Optional[float] = None) -> dict:
        """Return gaze direction and sustained off-center duration.

        `landmarks` must be one face's normalized MediaPipe Face Mesh landmarks.
        Pass None when no face is available; the gaze timer will be reset.
        """
        timestamp = monotonic() if now is None else now
        if not isfinite(timestamp):
            raise ValueError("now must be a finite timestamp")

        if landmarks is None:
            self._away_since = None
            return {"direction": "CENTER", "is_away": False, "duration": 0.0}

        required_index = max(index for eye in self.EYE_CORNERS for index in eye)
        if len(landmarks) <= required_index:
            raise ValueError(
                f"expected at least {required_index + 1} face landmarks, got {len(landmarks)}"
            )

        eye_ratios = []
        for outer_index, inner_index, iris_index in self.EYE_CORNERS:
            outer_x = self._x(landmarks[outer_index])
            inner_x = self._x(landmarks[inner_index])
            iris_x = self._x(landmarks[iris_index])
            eye_width = abs(inner_x - outer_x)
            if eye_width == 0:
                raise ValueError("eye-corner landmarks must have distinct x coordinates")
            eye_ratios.append((iris_x - min(outer_x, inner_x)) / eye_width)

        horizontal_ratio = sum(eye_ratios) / len(eye_ratios)
        if horizontal_ratio < 0.35:
            direction = "LOOKING_LEFT"
        elif horizontal_ratio > 0.65:
            direction = "LOOKING_RIGHT"
        else:
            direction = "CENTER"

        if direction == "CENTER":
            self._away_since = None
            duration = 0.0
        else:
            if self._away_since is None:
                self._away_since = timestamp
            duration = max(0.0, timestamp - self._away_since)

        return {
            "direction": direction,
            "is_away": direction != "CENTER" and duration >= self.away_threshold,
            "duration": duration,
        }

    @staticmethod
    def _x(landmark) -> float:
        try:
            x = float(landmark.x)
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError("face landmarks must have numeric x coordinates") from exc
        if not isfinite(x):
            raise ValueError("face landmark x coordinates must be finite")
        return x
