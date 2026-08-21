import asyncio
import enum
import logging
import queue
import re
import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional, Any

from simulator.config import TTS_ENGINE

logger = logging.getLogger("SmartGlasses.Speaker")


class TTSState(str, enum.Enum):
    """Explicit lifecycle states for Text-To-Speech pipeline."""
    IDLE = "IDLE"
    QUEUED = "QUEUED"
    SPEAKING = "SPEAKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TTSError(RuntimeError):
    """Raised when Text-To-Speech engine fails during initialization or playback."""
    pass


def sanitize_speech_text(text: str) -> str:
    """Cleans markdown formatting and extraneous characters for clean speech synthesis."""
    if not text:
        return ""
    # Strip markdown bold, italics, inline code, headers, bullets
    cleaned = re.sub(r"(\*\*|\*|__|_|`|#+)", "", text)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    # Normalize whitespace and newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class TextToSpeechEngine(ABC):
    @abstractmethod
    async def speak(self, text: str) -> float:
        """Synthesize and play audio. Returns latency in ms."""
        pass


class SimulatorTextToSpeech(TextToSpeechEngine):
    """
    Deterministic Text-to-Speech service with a single background worker thread and queue.
    
    Guarantees:
    1. Deterministic execution: SAPI COM objects are initialized in a dedicated STA thread.
    2. Single worker queue: Overlapping speech operations are serialized in FIFO order.
    3. Blocking playback: Future resolves only after playback is fully completed.
    4. State machine: IDLE -> QUEUED -> SPEAKING -> COMPLETED / FAILED.
    5. Structured logging: TTS_START, TTS_ENGINE_READY, TTS_TEXT_RECEIVED,
       TTS_PLAYBACK_START, TTS_PLAYBACK_COMPLETE, TTS_ERROR.
    6. Robust error reporting: Exceptions are captured, state set to FAILED, and raised to caller.
    """

    def __init__(self, engine_type: str = TTS_ENGINE, silent: bool = False, rate: int = 175):
        self.engine_type = engine_type.lower() if engine_type else "sapi5"
        self.silent = silent or (self.engine_type == "silent")
        self.rate = rate
        self._state: TTSState = TTSState.IDLE
        self._state_lock = threading.Lock()

        logger.info(
            "TTS_START: Initializing Smart Glasses TTS system (engine=%s, silent=%s, rate=%d)",
            self.engine_type,
            self.silent,
            self.rate
        )

        # Work queue and worker thread
        self._queue: queue.Queue = queue.Queue()
        self._ready_event = threading.Event()
        self._init_error: Optional[Exception] = None
        self._stopped = False

        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="SimulatorTTS-Worker",
            daemon=True
        )
        self._worker_thread.start()

        # Wait for worker thread engine initialization
        self._ready_event.wait(timeout=5.0)
        if self._init_error:
            self._set_state(TTSState.FAILED)
            logger.error("TTS_ERROR: TTS Engine initialization failed: %s", self._init_error)
            raise TTSError(f"TTS Engine initialization failed: {self._init_error}") from self._init_error

    @property
    def state(self) -> TTSState:
        with self._state_lock:
            return self._state

    def _set_state(self, new_state: TTSState):
        with self._state_lock:
            self._state = new_state

    def _worker_loop(self):
        """Dedicated STA worker loop for audio playback."""
        engine_instance: Any = None
        engine_name = "silent"

        try:
            if not self.silent:
                if self.engine_type in ("sapi5", "sapi", "windows"):
                    try:
                        import pythoncom
                        import win32com.client
                        pythoncom.CoInitialize()
                        engine_instance = win32com.client.Dispatch("SAPI.SpVoice")
                        engine_instance.Rate = 1  # 0 is normal, 1 is slightly faster
                        engine_name = "sapi5"
                        logger.info("TTS_ENGINE_READY: Native Windows SAPI5 SpVoice initialized successfully.")
                    except Exception as sapi_err:
                        logger.warning("SAPI5 initialization failed (%s), attempting pyttsx3 fallback...", sapi_err)
                        import pyttsx3
                        engine_instance = pyttsx3.init()
                        engine_instance.setProperty("rate", self.rate)
                        engine_name = "pyttsx3"
                        logger.info("TTS_ENGINE_READY: pyttsx3 fallback initialized successfully.")
                elif self.engine_type == "pyttsx3":
                    import pyttsx3
                    engine_instance = pyttsx3.init()
                    engine_instance.setProperty("rate", self.rate)
                    engine_name = "pyttsx3"
                    logger.info("TTS_ENGINE_READY: pyttsx3 initialized successfully.")
                else:
                    logger.info("TTS_ENGINE_READY: Custom engine '%s' running in simulated mode.", self.engine_type)
            else:
                logger.info("TTS_ENGINE_READY: Silent TTS mode active.")
        except Exception as e:
            self._init_error = e
            self._ready_event.set()
            return

        self._ready_event.set()

        # Process speech synthesis items from queue
        while True:
            item = self._queue.get()
            if item is None or self._stopped:
                self._queue.task_done()
                break

            text, loop, future, timestamp = item

            # Update state to SPEAKING
            self._set_state(TTSState.SPEAKING)
            sample_preview = text[:50] + ("..." if len(text) > 50 else "")
            logger.info("TTS_PLAYBACK_START: Playing audio for text: '%s'", sample_preview)

            t_play_start = time.time()
            try:
                if self.silent:
                    # Silent mode: instant deterministic completion
                    time.sleep(0.005)
                elif engine_name == "sapi5":
                    # Flag 0 = SVSFDefault (synchronous, blocks until playback finishes)
                    engine_instance.Speak(text, 0)
                elif engine_name == "pyttsx3":
                    engine_instance.say(text)
                    engine_instance.runAndWait()
                else:
                    time.sleep(0.01)

                duration_ms = (time.time() - timestamp) * 1000.0
                self._set_state(TTSState.COMPLETED)
                logger.info("TTS_PLAYBACK_COMPLETE: Finished speech playback in %.2f ms", duration_ms)

                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, duration_ms)
            except Exception as ex:
                self._set_state(TTSState.FAILED)
                err_msg = f"TTS playback failed on text '{sample_preview}': {ex}"
                logger.error("TTS_ERROR: %s", err_msg)
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, TTSError(err_msg))
            finally:
                self._queue.task_done()
                # If queue is empty, transition to IDLE
                if self._queue.empty():
                    self._set_state(TTSState.IDLE)

        # Cleanup on shutdown
        if engine_name == "sapi5":
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass

    async def speak(self, text: str, timeout: Optional[float] = None) -> float:
        """
        Enqueues text for playback and awaits full completion.
        
        Returns:
            duration_ms: Total latency from queue submission to playback completion.
        Raises:
            TTSError: If audio synthesis/playback encounters an error.
            asyncio.TimeoutError: If playback exceeds the specified timeout.
        """
        if self._stopped:
            self._set_state(TTSState.FAILED)
            raise TTSError("Cannot speak: TTS engine is stopped.")

        clean_text = sanitize_speech_text(text)
        if not clean_text:
            logger.info("TTS_TEXT_RECEIVED: Received empty text, skipping playback.")
            return 0.0

        logger.info(
            "TTS_TEXT_RECEIVED: Received text (%d chars): '%s'",
            len(clean_text),
            clean_text[:60] + ("..." if len(clean_text) > 60 else "")
        )

        self._set_state(TTSState.QUEUED)
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        submission_time = time.time()

        self._queue.put((clean_text, loop, future, submission_time))

        try:
            if timeout:
                return await asyncio.wait_for(future, timeout=timeout)
            return await future
        except asyncio.TimeoutError:
            self._set_state(TTSState.FAILED)
            logger.error("TTS_ERROR: Speech playback timed out after %s seconds.", timeout)
            raise
        except Exception as e:
            self._set_state(TTSState.FAILED)
            logger.error("TTS_ERROR: Exception during TTS speak: %s", e)
            raise

    def stop(self):
        """Stops the worker thread and cleans up resources."""
        if not self._stopped:
            self._stopped = True
            self._queue.put(None)
            if self._worker_thread.is_alive():
                self._worker_thread.join(timeout=3.0)
            self._set_state(TTSState.IDLE)

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass
