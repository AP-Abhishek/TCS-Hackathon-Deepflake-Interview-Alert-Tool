"""
proctor/audio.py
----------------
Responsible: Person 2 (Lip Dynamics & Audio Energy Monitoring)

TASK OBJECTIVE:
- Continuously sample microphone input in a non-blocking background thread.
- Compute current Audio RMS energy level.
- Provide real-time speech activity status for cross-modal correlation with lip movement:
    1. Whispering Detection: Lips moving + Mic volume near zero.
    2. External Prompter Detection: Mic volume high + Lips static.

TODO for Person 2:
1. Initialize sounddevice.InputStream with a callback function.
2. In the callback, compute RMS = sqrt(mean(audio_chunk**2)).
3. Compare RMS against speech_threshold to set is_speaking = True / False.
4. Provide thread-safe get_status() method returning current volume and speaking flag.
5. Handle exceptions gracefully if no microphone is connected.
"""

import threading
import numpy as np

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False


class AudioMonitor:
    def __init__(self, speech_threshold: float = 0.015, sample_rate: int = 16000):
        """
        TODO:
        - Store speech threshold and sample rate.
        - Initialize stream state and volume tracking variables.
        """
        self.speech_threshold = speech_threshold
        self.sample_rate = sample_rate
        self.current_volume = 0.0
        self.is_speaking = False
        self.running = False
        self.stream = None
        self._lock = threading.Lock()

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Compute RMS of incoming audio buffer in real time.
        Thread-safely update self.current_volume and self.is_speaking.
        """
        if indata is not None and len(indata) > 0:
            rms = np.sqrt(np.mean(indata**2))
            vol = float(rms)
            speaking = vol > self.speech_threshold
            with self._lock:
                self.current_volume = vol
                self.is_speaking = speaking

    def start(self):
        """
        TODO:
        - Start sounddevice InputStream in background.
        """
        if not AUDIO_AVAILABLE or self.running:
            return

        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=1024,
                callback=self._audio_callback
            )
            self.stream.start()
            self.running = True
        except Exception as e:
            print(f"[AudioMonitor] Warning: Microphone unavailable ({e}). Continuing in silent mode.")
            self.running = False

    def stop(self):
        """
        TODO:
        - Gracefully stop and close audio stream.
        """
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.running = False

    def get_status(self) -> dict:
        """
        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "volume": float,        # Current RMS volume level
            "is_speaking": bool,   # True if volume > speech_threshold
            "available": bool      # True if mic is actively recording
        }
        """
        with self._lock:
            vol = round(self.current_volume, 4)
            speaking = self.is_speaking
        return {
            "volume": vol,
            "is_speaking": speaking,
            "available": self.running
        }
