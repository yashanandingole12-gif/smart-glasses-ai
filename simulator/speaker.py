import asyncio
import subprocess
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional
from simulator.config import TTS_ENGINE

logger = logging.getLogger("SmartGlasses.Speaker")

class TextToSpeechEngine(ABC):
    @abstractmethod
    async def speak(self, text: str) -> float:
        """Synthesize and play audio. Returns latency in ms."""
        pass

class SimulatorTextToSpeech(TextToSpeechEngine):
    def __init__(self, engine_type: str = TTS_ENGINE, silent: bool = False):
        self.silent = silent or (engine_type.lower() == "silent")
        self.engine_type = engine_type.lower()
        self._pyttsx3_engine = None

        if not self.silent and self.engine_type == "pyttsx3":
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        try:
            import pyttsx3
            self._pyttsx3_engine = pyttsx3.init()
            self._pyttsx3_engine.setProperty('rate', 175)
        except Exception as e:
            logger.warning(f"pyttsx3 init failed ({e}). SAPI5 fallback will be used.")
            self._pyttsx3_engine = None

    async def speak(self, text: str) -> float:
        t0 = time.time()
        if self.silent:
            return (time.time() - t0) * 1000.0

        loop = asyncio.get_event_loop()

        # 1. If pyttsx3 configured and available
        if self.engine_type == "pyttsx3" and self._pyttsx3_engine is not None:
            try:
                def _speak_pyttsx3():
                    self._pyttsx3_engine.say(text)
                    self._pyttsx3_engine.runAndWait()

                await loop.run_in_executor(None, _speak_pyttsx3)
                duration_ms = (time.time() - t0) * 1000.0
                return duration_ms
            except Exception as ex:
                logger.warning(f"pyttsx3 speech failed ({ex}), falling back to SAPI5.")

        # 2. Windows SAPI5 (Default & Low Latency on Windows)
        try:
            def _speak_sapi5():
                clean_text = text.replace('"', '`"').replace("'", "''")
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak(\\"{clean_text}\\")"'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=8)

            await loop.run_in_executor(None, _speak_sapi5)
            duration_ms = (time.time() - t0) * 1000.0
            return duration_ms
        except Exception as ex:
            logger.error(f"SAPI5 TTS playback failed: {ex}")
            return (time.time() - t0) * 1000.0
