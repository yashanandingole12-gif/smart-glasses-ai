import asyncio
import io
import time
import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from simulator.config import STT_ENGINE, SAMPLE_RATE

logger = logging.getLogger("SmartGlasses.Microphone")

class SpeechToTextEngine(ABC):
    @abstractmethod
    async def transcribe_from_microphone(self, duration_sec: float = 3.5) -> Tuple[str, float]:
        """Record from microphone and return (transcribed_text, latency_ms)."""
        pass

class SimulatorSpeechToText(SpeechToTextEngine):
    def __init__(self, sample_rate: int = SAMPLE_RATE, engine_type: str = STT_ENGINE):
        self.sample_rate = sample_rate
        self.engine_type = engine_type.lower()
        self._whisper_model = None
        if self.engine_type in ["faster_whisper", "auto"]:
            self._init_whisper()

    def _init_whisper(self):
        try:
            from faster_whisper import WhisperModel
            logger.info("Loading faster-whisper (tiny.en) for real-time local STT...")
            # Use int8 CPU compute for instant transcription
            self._whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            logger.info("faster-whisper (tiny.en) loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize faster-whisper ({e}). Fallback transcription will be used.")
            self._whisper_model = None

    async def record_audio_chunk(self, duration_sec: float = 3.5) -> Optional[np.ndarray]:
        """Record live audio chunk from laptop microphone using sounddevice."""
        try:
            import sounddevice as sd
            loop = asyncio.get_event_loop()
            recording = await loop.run_in_executor(
                None,
                lambda: sd.rec(
                    int(duration_sec * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32"
                )
            )
            sd.wait()
            audio_flat = recording.flatten()
            # Calculate audio energy / RMS
            rms = np.sqrt(np.mean(audio_flat**2))
            logger.info(f"Recorded {duration_sec}s audio (RMS Level: {rms:.4f})")
            return audio_flat
        except Exception as e:
            logger.error(f"Live microphone recording error: {e}")
            return None

    async def transcribe_from_microphone(self, duration_sec: float = 3.5) -> Tuple[str, float]:
        t0 = time.time()

        if self.engine_type == "mock":
            return "Good morning.", (time.time() - t0) * 1000.0

        audio_data = await self.record_audio_chunk(duration_sec)

        if audio_data is not None and self._whisper_model is not None:
            try:
                import soundfile as sf
                wav_io = io.BytesIO()
                sf.write(wav_io, audio_data, self.sample_rate, format='WAV')
                wav_io.seek(0)

                t_infer_start = time.time()
                loop = asyncio.get_event_loop()
                segments, _ = await loop.run_in_executor(
                    None,
                    lambda: self._whisper_model.transcribe(wav_io, beam_size=1, language="en")
                )
                text = " ".join([seg.text for seg in segments]).strip()
                t_total_stt = (time.time() - t0) * 1000.0

                if text:
                    logger.info(f"STT Transcript: '{text}' in {t_total_stt:.1f}ms")
                    return text, t_total_stt
                else:
                    logger.info("No audible speech detected, default fallback applied.")
                    return "Good morning.", t_total_stt
            except Exception as ex:
                logger.error(f"STT transcription failed: {ex}")

        # Fallback default
        return "Good morning.", (time.time() - t0) * 1000.0
