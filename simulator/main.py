import asyncio
import time
import sys
import uuid
import httpx
from typing import List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from simulator.config import BACKEND_URL, DEFAULT_CITY, DEFAULT_COUNTRY, STT_ENGINE, TTS_ENGINE
from simulator.device import SimulatedGlassesDevice, DeviceEvent, DeviceCommand
from simulator.microphone import SimulatorSpeechToText
from simulator.speaker import SimulatorTextToSpeech
from simulator.camera import SimulatorCamera
from simulator.context import SimulatorContextEngine
from simulator.keyboard_handler import KeyboardHandler

console = Console()

class SmartGlassesSimulatorApp:
    def __init__(self):
        self.device = SimulatedGlassesDevice(initial_battery=82)
        self.microphone = SimulatorSpeechToText(engine_type=STT_ENGINE)
        self.speaker = SimulatorTextToSpeech(engine_type=TTS_ENGINE)
        self.camera = SimulatorCamera()
        self.context_engine = SimulatorContextEngine(city=DEFAULT_CITY, country=DEFAULT_COUNTRY)
        self.session_id = str(uuid.uuid4())
        self.backend_connected = False
        self.conversation_history: List[Tuple[str, str]] = []
        self.keyboard_handler = None
        self._busy = False

    async def check_backend(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{BACKEND_URL}/api/v1/health")
                if resp.status_code == 200:
                    self.backend_connected = True
                    return True
        except Exception:
            self.backend_connected = False
        return False

    def render_ui(self):
        console.clear()
        time_info = self.context_engine.get_current_time()

        ui_text = f"""
[bold cyan]=========================================[/bold cyan]
[bold white] CONTEXT-AWARE SMART GLASSES SIMULATOR[/bold white]
[bold cyan]=========================================[/bold cyan]

[bold yellow]Device:[/bold yellow]
CONNECTED (SIMULATED ESP32)

[bold yellow]Battery:[/bold yellow]
{self.device.get_battery()}%

[bold yellow]Microphone (STT):[/bold yellow]
[green]READY ({STT_ENGINE})[/green]

[bold yellow]Speaker (TTS):[/bold yellow]
[green]READY ({TTS_ENGINE})[/green]

[bold yellow]Camera:[/bold yellow]
[green]READY[/green]

[bold yellow]Backend:[/bold yellow]
{"[green]CONNECTED[/green]" if self.backend_connected else "[red]DISCONNECTED (Run ./scripts/run_backend.ps1)[/red]"}

[bold yellow]Agent:[/bold yellow]
[green]READY[/green]

[bold yellow]Location:[/bold yellow]
{self.context_engine.city}

[bold yellow]Time:[/bold yellow]
{time_info['local_time']} ({time_info['period'].capitalize()})

[bold cyan]-----------------------------------------[/bold cyan]

[bold green]Press ENTER to talk[/bold green] (or type a message)
[bold blue]Press C for camera[/bold blue]
[bold magenta]Press B for device status[/bold magenta]
[bold red]Press Q to quit[/bold red]

[bold cyan]-----------------------------------------[/bold cyan]

[bold white]Conversation:[/bold white]
"""
        console.print(ui_text)

        for role, msg in self.conversation_history[-4:]:
            if role == "USER":
                console.print(f"\n[bold green]USER:[/bold green]\n{msg}")
            elif role == "ASSISTANT":
                console.print(f"\n[bold cyan]ASSISTANT:[/bold cyan]\n{msg}")
            elif role == "SYSTEM":
                console.print(f"\n[bold yellow]SYSTEM:[/bold yellow]\n{msg}")

        console.print("\n[bold cyan]=========================================[/bold cyan]\n")

    async def handle_button_press(self, explicit_text: str = None):
        """Simulates physical glasses push-to-talk button press."""
        if self._busy:
            return
        self._busy = True

        t_button_pressed = time.time()
        self.device.trigger_button_press()
        console.print("\n[bold yellow]🎙️  [BUTTON PRESSED] Listening on laptop microphone... Speak now![/bold yellow]")

        transcript = ""
        stt_duration_ms = 0.0

        if explicit_text:
            transcript = explicit_text
            stt_duration_ms = 5.0
        else:
            # Record live audio and transcribe
            transcript, stt_duration_ms = await self.microphone.transcribe_from_microphone(duration_sec=3.0)

        self.conversation_history.append(("USER", transcript))
        self.render_ui()

        # Send request to FastAPI backend
        t_req_start = time.time()
        context_payload = self.context_engine.get_full_context_dict(battery=self.device.get_battery())

        payload = {
            "session_id": self.session_id,
            "message": transcript,
            "context": context_payload,
            "client_timestamp": time.time()
        }

        assistant_reply = "I could not reach the backend."
        backend_metadata = {}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{BACKEND_URL}/api/v1/agent/message", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    assistant_reply = data.get("response", "Ready.")
                    backend_metadata = data.get("metadata", {})
                else:
                    assistant_reply = f"Error from backend: HTTP {resp.status_code}"
        except Exception as e:
            assistant_reply = f"Backend connection failed: {e}"

        backend_duration_ms = (time.time() - t_req_start) * 1000.0

        self.conversation_history.append(("ASSISTANT", assistant_reply))
        self.render_ui()

        # Play TTS through laptop speaker with TTFA measurement
        console.print("[bold cyan]🔊 [SPEAKER] Speaking response through laptop speaker...[/bold cyan]")
        ttfa_ms = 0.0
        tts_playback_ms = 0.0
        try:
            ttfa_ms, tts_playback_ms = await self.speaker.speak_measured(assistant_reply)
        except Exception as e:
            console.print(f"[bold red]❌ [SPEAKER ERROR] TTS Playback failed: {e}[/bold red]")

        total_request_ms = stt_duration_ms + backend_duration_ms + ttfa_ms
        total_turn_ms = (time.time() - t_button_pressed) * 1000.0

        # Detailed Latency Breakdown
        console.print(
            f"\n[bold green]⏱️  Latency Metrics:[/bold green]\n"
            f"   • STT (Microphone & Inference):  {stt_duration_ms:.1f}ms\n"
            f"   • Backend Context & Calendar:    {backend_duration_ms:.1f}ms\n"
            f"   • Time-to-First-Audio (TTFA):    {ttfa_ms:.1f}ms\n"
            f"   • [bold]TOTAL REQUEST TIME (to Audio):[/bold] [bold green]{total_request_ms:.1f}ms ({total_request_ms/1000.0:.2f}s)[/bold green]\n"
            f"   • TTS Full Playback Duration:    {tts_playback_ms:.1f}ms ({tts_playback_ms/1000.0:.2f}s)\n"
            f"   • [bold]TOTAL END-TO-END TURN:[/bold]          [bold cyan]{total_turn_ms/1000.0:.2f}s ({total_turn_ms:.1f}ms)[/bold cyan]\n"
        )

        self._busy = False


    async def handle_camera_press(self):
        """Simulates camera snapshot button."""
        if self._busy:
            return
        self._busy = True
        console.print("[yellow]📷 [CAMERA] Capturing snapshot from webcam...[/yellow]")
        success, path, b64_str = self.camera.capture_image()
        if success:
            console.print(f"[green]Captured image saved to: {path}[/green]")
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"{BACKEND_URL}/api/v1/vision/analyze",
                        json={"session_id": self.session_id, "image_base64": b64_str}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        desc = data.get("description", "Image analyzed.")
                        self.conversation_history.append(("SYSTEM", f"Camera Vision: {desc}"))
                        self.render_ui()
                        await self.speaker.speak(f"I see: {desc}")
            except Exception as e:
                console.print(f"[red]Vision analysis failed: {e}[/red]")
        self._busy = False

    def handle_battery_press(self):
        console.print(f"[bold magenta]🔋 Device Status: Battery at {self.device.get_battery()}%, BLE: Ready, Sensors: OK[/bold magenta]")

    def handle_quit(self):
        console.print("[bold red]Shutting down Smart Glasses Simulator. Goodbye![/bold red]")
        self.speaker.stop()
        sys.exit(0)

    async def run(self):
        await self.check_backend()
        await self.device.connect()
        self.render_ui()

        # Start standard input loop
        self.keyboard_handler = KeyboardHandler(
            on_button_press=lambda: asyncio.create_task(self.handle_button_press()),
            on_camera_press=lambda: asyncio.create_task(self.handle_camera_press()),
            on_battery_press=self.handle_battery_press,
            on_quit=self.handle_quit,
            on_text_input=lambda text: asyncio.create_task(self.handle_button_press(explicit_text=text))
        )

        await self.keyboard_handler.run_input_loop()

if __name__ == "__main__":
    app = SmartGlassesSimulatorApp()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass
