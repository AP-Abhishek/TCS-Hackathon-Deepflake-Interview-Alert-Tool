"""
proctor/audio.py
----------------
Responsible: Person 2 (Lip Dynamics, Audio Energy & Live Speech Transcription)

Features:
- Continuously samples microphone input in a non-blocking background thread.
- Computes real-time Audio RMS energy level.
- Live speech buffering and background transcription using SpeechRecognition.
- Provides real-time transcript & audio volume meter for HUD and answer evaluation.
"""

import queue
import threading
import time
import numpy as np

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except Exception:
    SR_AVAILABLE = False


class AudioMonitor:
    def __init__(self, speech_threshold: float = 0.015, sample_rate: int = 16000):
        self.speech_threshold = speech_threshold
        self.sample_rate = sample_rate
        self.current_volume = 0.0
        self.is_speaking = False
        self.running = False
        self.stream = None
        self._lock = threading.Lock()

        # Speech Recording & Transcription state
        self.recording_enabled = True
        self._speech_buffer = []
        self._silence_frames = 0
        self._speaking_frames = 0
        self._transcript_parts = []
        self._transcribe_queue = queue.Queue()
        self._transcriber_thread = None
        self._last_speech_time = None
        self._has_spoken_for_q = False

        if SR_AVAILABLE:
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = False
        else:
            self._recognizer = None

    def _audio_callback(self, indata, frames, time_info, status):
        if indata is None or len(indata) == 0:
            return

        rms = float(np.sqrt(np.mean(indata**2)))
        speaking = rms > self.speech_threshold

        with self._lock:
            self.current_volume = rms
            self.is_speaking = speaking

            if self.recording_enabled:
                pcm_data = (indata[:, 0] * 32767).clip(-32768, 32767).astype(np.int16).tobytes()

                if speaking:
                    self._speech_buffer.append(pcm_data)
                    self._speaking_frames += 1
                    self._silence_frames = 0
                    self._last_speech_time = time.time()
                    self._has_spoken_for_q = True
                else:
                    if len(self._speech_buffer) > 0:
                        self._speech_buffer.append(pcm_data)
                        self._silence_frames += 1

                        # If silence persists for ~1.0s (approx 16 chunks at 1024 samples @ 16kHz)
                        # and we have at least ~0.5s of audio, enqueue for transcription
                        if self._silence_frames > 15 and len(self._speech_buffer) > 8:
                            full_pcm = b"".join(self._speech_buffer)
                            self._speech_buffer = []
                            self._silence_frames = 0
                            self._speaking_frames = 0
                            self._transcribe_queue.put(full_pcm)

    def _transcriber_worker(self):
        while self.running:
            try:
                pcm_bytes = self._transcribe_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if not pcm_bytes or not SR_AVAILABLE or self._recognizer is None:
                continue

            try:
                audio_data = sr.AudioData(pcm_bytes, self.sample_rate, 2)
                text = self._recognizer.recognize_google(audio_data)
                text = text.strip()
                if text:
                    with self._lock:
                        self._transcript_parts.append(text)
            except (sr.UnknownValueError, sr.RequestError):
                pass
            except Exception:
                pass

    def start(self):
        if not AUDIO_AVAILABLE or self.running:
            return

        try:
            self.running = True
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=1024,
                dtype="float32",
                callback=self._audio_callback
            )
            self.stream.start()

            if SR_AVAILABLE:
                self._transcriber_thread = threading.Thread(
                    target=self._transcriber_worker,
                    name="audio-transcriber",
                    daemon=True
                )
                self._transcriber_thread.start()
        except Exception as e:
            print(f"[AudioMonitor] Warning: Microphone unavailable ({e}). Continuing in silent mode.")
            self.running = False

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def set_recording_enabled(self, enabled: bool):
        with self._lock:
            self.recording_enabled = enabled
            if not enabled:
                if len(self._speech_buffer) > 8:
                    full_pcm = b"".join(self._speech_buffer)
                    self._transcribe_queue.put(full_pcm)
                self._speech_buffer = []
                self._silence_frames = 0

    def get_transcript(self) -> str:
        with self._lock:
            return " ".join(self._transcript_parts).strip()

    def clear_transcript(self):
        with self._lock:
            self._transcript_parts = []
            self._speech_buffer = []
            self._silence_frames = 0
            self._speaking_frames = 0
            self._last_speech_time = None
            self._has_spoken_for_q = False

    def get_silence_after_speech(self) -> float:
        """Returns seconds of silence elapsed since candidate stopped speaking (or 0.0 if not spoken)."""
        with self._lock:
            if not self._has_spoken_for_q or self.is_speaking or self._last_speech_time is None:
                return 0.0
            return time.time() - self._last_speech_time

    def get_status(self) -> dict:
        """
        RETURN CONTRACT (DO NOT CHANGE EXISTING KEYS):
        {
            "volume": float,        # Current RMS volume level
            "is_speaking": bool,   # True if volume > speech_threshold
            "available": bool,     # True if mic is actively recording
            "transcript": str      # Live accumulated transcript
        }
        """
        with self._lock:
            vol = round(self.current_volume, 4)
            speaking = self.is_speaking
            transcript = " ".join(self._transcript_parts).strip()
        return {
            "volume": vol,
            "is_speaking": speaking,
            "available": self.running,
            "transcript": transcript
        }
