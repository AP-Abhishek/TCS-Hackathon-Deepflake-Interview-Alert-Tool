"""
interview/speaker.py
--------------------
Non-blocking text-to-speech for the AI interviewer (pyttsx3, fully offline).

Design notes
- pyttsx3 engines are not thread-safe, so ONE worker thread creates and owns the
  engine; callers only push text onto a queue. The OpenCV loop never blocks.
- Utterances play in order. is_speaking() stays True until the queue is empty.
- speaking_ended_at is a time.monotonic() timestamp of the last finished
  utterance. The proctoring module uses it as the start of the answer window,
  and should ignore microphone input while is_speaking() is True (the mic
  would otherwise hear the agent and report "audio without lip movement").
- If the TTS engine cannot start, the speaker degrades to silent mode and the
  interview continues with on-screen text only.
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

_STOP = object()


class AgentSpeaker:
    def __init__(
        self,
        rate: int = 175,
        volume: float = 1.0,
        voice_hint: Optional[str] = None,
        engine_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        rate / volume   pyttsx3 speech rate (words per minute) and volume 0.0-1.0.
        voice_hint      case-insensitive substring of a voice name, e.g. "zira" or "female".
        engine_factory  returns a pyttsx3-compatible engine; used for tests.
        """
        self._rate = rate
        self._volume = min(max(volume, 0.0), 1.0)
        self._voice_hint = voice_hint.lower() if voice_hint else None
        self._engine_factory = engine_factory

        self._queue: "queue.Queue[Any]" = queue.Queue()
        self._lock = threading.Lock()
        self._pending = 0
        self._idle = threading.Event()
        self._idle.set()
        self._last_finished_at: Optional[float] = None
        self._available = False
        self._ready = threading.Event()
        self._closed = False

        self._thread = threading.Thread(target=self._run, name="agent-speaker", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5.0)  # know early whether speech works

    # ------------------------------------------------------------------ public API

    @property
    def available(self) -> bool:
        """False when the TTS engine failed to start (silent mode)."""
        return self._available

    @property
    def speaking_ended_at(self) -> Optional[float]:
        """time.monotonic() when the speaker last became idle, or None if it never spoke."""
        with self._lock:
            return self._last_finished_at

    def speak_async(self, text: str, on_finish: Optional[Callable[[], None]] = None) -> None:
        """Queue `text` to be spoken and return immediately.

        on_finish runs on the speaker thread after this utterance; keep it short.
        """
        text = " ".join((text or "").split())
        if not text or self._closed:
            return
        with self._lock:
            self._pending += 1
            self._idle.clear()
        self._queue.put((text, on_finish))

    def is_speaking(self) -> bool:
        """True while an utterance is playing or still queued."""
        return not self._idle.is_set()

    def wait_until_done(self, timeout: Optional[float] = None) -> bool:
        """Block until all queued speech finished. Returns False on timeout."""
        return self._idle.wait(timeout)

    def shutdown(self, timeout: float = 2.0) -> None:
        """Finish queued speech, then stop the worker thread."""
        if self._closed:
            return
        self._closed = True
        self._queue.put(_STOP)
        self._thread.join(timeout)

    def __enter__(self) -> "AgentSpeaker":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.shutdown()

    # ------------------------------------------------------------------ worker

    def _run(self) -> None:
        engine = self._start_engine()
        self._ready.set()
        while True:
            item = self._queue.get()
            if item is _STOP:
                break
            text, on_finish = item
            try:
                if engine is not None:
                    engine.say(text)
                    engine.runAndWait()
            except Exception:
                logger.exception("Speech failed for one utterance")
            finally:
                self._mark_done()
            if on_finish is not None:
                try:
                    on_finish()
                except Exception:
                    logger.exception("on_finish callback raised")
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                logger.debug("Engine stop failed", exc_info=True)

    def _start_engine(self) -> Optional[Any]:
        try:
            if self._engine_factory is not None:
                engine = self._engine_factory()
            else:
                import pyttsx3  # imported here so the module loads without it

                engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            engine.setProperty("volume", self._volume)
            self._select_voice(engine)
            self._available = True
            return engine
        except Exception:
            logger.warning("Text-to-speech unavailable; continuing in silent mode", exc_info=True)
            return None

    def _select_voice(self, engine: Any) -> None:
        if not self._voice_hint:
            return
        for voice in engine.getProperty("voices") or []:
            if self._voice_hint in (getattr(voice, "name", "") or "").lower():
                engine.setProperty("voice", voice.id)
                return
        logger.info("No voice matched %r; using the system default", self._voice_hint)

    def _mark_done(self) -> None:
        with self._lock:
            self._pending -= 1
            if self._pending == 0:
                self._last_finished_at = time.monotonic()
                self._idle.set()


if __name__ == "__main__":  # smoke test: python -m interview.speaker
    logging.basicConfig(level=logging.INFO)
    with AgentSpeaker() as speaker:
        speaker.speak_async("Hello. This is a test of the interview speaker.")
        print("speaking:", speaker.is_speaking(), "(this line prints immediately)")
        speaker.wait_until_done(timeout=15)
        print("done, silent mode:", not speaker.available)