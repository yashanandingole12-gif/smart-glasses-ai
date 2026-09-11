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
        self._whisper_initialized = False

    def _ensure_whisper(self):
        if self._whisper_initialized:
            return
        self._whisper_initialized = True
        if self.engine_type in ["faster_whisper", "auto"]:
            try:
                from faster_whisper import WhisperModel
                logger.info("Loading faster-whisper (tiny.en) with int8 CPU threads=4...")
                self._whisper_model = WhisperModel(
                    "tiny.en",
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=4
                )
                logger.info("faster-whisper (tiny.en) loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize faster-whisper ({e}). Fallback transcription will be used.")
                self._whisper_model = None

    async def record_audio_chunk(self, max_duration_sec: float = 3.0, silence_timeout_sec: float = 0.5) -> Optional[np.ndarray]:
        """
        Record live audio dynamically with Voice Activity Detection (VAD) / silence cutoff.
        Stops early when user finishes speaking instead of waiting for full duration.
        """
        try:
            import sounddevice as sd
            loop = asyncio.get_event_loop()

            def _record_sync():
                chunk_duration = 0.1  # 100ms slices
                chunk_samples = int(chunk_duration * self.sample_rate)
                recorded_chunks = []
                
                speech_detected = False
                silence_chunks = 0
                max_chunks = int(max_duration_sec / chunk_duration)
                silence_chunk_threshold = int(silence_timeout_sec / chunk_duration)
                energy_threshold = 0.008

                with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                    for _ in range(max_chunks):
                        data, _ = stream.read(chunk_samples)
                        chunk_flat = data.flatten()
                        recorded_chunks.append(chunk_flat)
                        
                        rms = float(np.sqrt(np.mean(chunk_flat**2)))
                        if rms > energy_threshold:
                            speech_detected = True
                            silence_chunks = 0
                        elif speech_detected:
                            silence_chunks += 1
                            if silence_chunks >= silence_chunk_threshold:
                                # Stop recording early
                                break

                if not recorded_chunks:
                    return None
                return np.concatenate(recorded_chunks)

            audio_data = await loop.run_in_executor(None, _record_sync)
            if audio_data is not None:
                duration_actual = len(audio_data) / self.sample_rate
                logger.info(f"Dynamic VAD recording complete ({duration_actual:.2f}s audio)")
            return audio_data

        except Exception as e:
            logger.error(f"Live microphone recording error: {e}")
            return None

    async def transcribe_from_microphone(self, duration_sec: float = 3.0) -> Tuple[str, float]:
        t0 = time.time()

        if self.engine_type == "mock":
            return "What do I have today?", (time.time() - t0) * 1000.0

        self._ensure_whisper()
        audio_data = await self.record_audio_chunk(max_duration_sec=duration_sec)

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
                    lambda: self._whisper_model.transcribe(
                        wav_io,
                        beam_size=1,
                        language="en",
                        temperature=0.0
                    )
                )
                text = " ".join([seg.text for seg in segments]).strip()
                t_total_stt = (time.time() - t0) * 1000.0

                if text:
                    logger.info(f"STT Transcript: '{text}' in {t_total_stt:.1f}ms")
                    return text, t_total_stt
                else:
                    logger.info("No audible speech detected.")
                    return "What do I have today?", t_total_stt
            except Exception as ex:
                logger.error(f"STT transcription failed: {ex}")

        # Fallback default
        return "What do I have today?", (time.time() - t0) * 1000.0

