import asyncio
import time
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table

from backend.app.config import settings
from backend.app.services.context_engine import context_engine
from backend.app.services.agent_graph import run_agent
from backend.app.services.llm_service import LLMService
from simulator.device import SimulatedGlassesDevice, DeviceEvent
from simulator.microphone import SimulatorSpeechToText
from simulator.speaker import SimulatorTextToSpeech
from simulator.context import SimulatorContextEngine

console = Console()
logging.basicConfig(level=logging.INFO)

async def run_live_pipeline():
    console.print("\n[bold cyan]==================================================================[/bold cyan]")
    console.print("[bold green]  SMART GLASSES AI ASSISTANT - LIVE GEMINI PIPELINE TEST  [/bold green]")
    console.print("[bold cyan]==================================================================[/bold cyan]\n")

    overall_start = time.perf_counter()

    # Step 1: Laptop Button Press
    t_btn_start = time.perf_counter()
    device = SimulatedGlassesDevice(initial_battery=85)
    btn_event = []
    device.register_event_listener(
        DeviceEvent.BUTTON_PRESSED,
        lambda d: btn_event.append("BUTTON_PRESSED")
    )
    await device.connect()
    device.trigger_button_press()
    t_btn_end = time.perf_counter()
    btn_latency_ms = (t_btn_end - t_btn_start) * 1000.0
    console.print(f"[bold yellow][1/7] Laptop Button Pressed[/bold yellow] (Event trigger latency: {btn_latency_ms:.2f} ms)")

    # Step 2: Microphone & STT
    console.print("[bold yellow][2/7] Microphone & STT: Listening on laptop microphone...[/bold yellow]")
    stt_engine = SimulatorSpeechToText(engine_type="faster_whisper")
    t_stt_start = time.perf_counter()
    transcript, stt_duration_ms = await stt_engine.transcribe_from_microphone(duration_sec=3.0)
    t_stt_end = time.perf_counter()
    console.print(f"      Transcript captured: [bold white]\"{transcript}\"[/bold white] ({stt_duration_ms:.2f} ms)")

    # Step 3: Context Engine Enrichment
    console.print("[bold yellow][3/7] Context Engine: Enriching temporal, location & calendar context...[/bold yellow]")
    t_ctx_start = time.perf_counter()
    sim_ctx_engine = SimulatorContextEngine(city="Nagpur", country="India")
    context_dict = sim_ctx_engine.get_full_context_dict(battery=device.get_battery())
    t_ctx_end = time.perf_counter()
    ctx_latency_ms = (t_ctx_end - t_ctx_start) * 1000.0
    time_info = context_dict["time"]
    loc_info = context_dict["location"]
    console.print(f"      Context retrieved: [bold white]{loc_info['city']}, {time_info['local_time']} ({time_info['period']})[/bold white] ({ctx_latency_ms:.2f} ms)")

    # Step 4 & 5: LangGraph & Gemini API Call (Measure Gemini Latency separately)
    console.print(f"[bold yellow][4/7] LangGraph & [5/7] Gemini API ({settings.LLM_MODEL}): Generating response...[/bold yellow]")
    
    # We also measure standalone Gemini inference time
    standalone_llm = LLMService(provider="gemini")
    t_gemini_start = time.perf_counter()
    # Execute full LangGraph flow with Gemini
    agent_output = await run_agent(
        session_id="live_pipeline_test_session",
        user_message=transcript,
        context_payload=context_dict
    )
    t_gemini_end = time.perf_counter()
    gemini_latency_ms = (t_gemini_end - t_gemini_start) * 1000.0

    response_text = agent_output.get("response", "")
    console.print(f"      [bold cyan]Agent Response:[/bold cyan] \"{response_text}\"")
    console.print(f"      [bold magenta]Gemini Inference Latency:[/bold magenta] [bold]{gemini_latency_ms:.2f} ms ({gemini_latency_ms/1000.0:.3f} s)[/bold]")

    # Step 6: Text-to-Speech (TTS)
    console.print("[bold yellow][6/7] TTS Playback: Synthesizing and speaking response through laptop speaker...[/bold yellow]")
    speaker = SimulatorTextToSpeech(engine_type="sapi5")
    t_tts_start = time.perf_counter()
    tts_duration_ms = await speaker.speak(response_text)
    t_tts_end = time.perf_counter()
    console.print(f"      TTS synthesized and played ({tts_duration_ms:.2f} ms)")

    overall_total_ms = (time.perf_counter() - overall_start) * 1000.0

    # Summary Table
    table = Table(title="Live Pipeline Latency Breakdown", show_header=True, header_style="bold green")
    table.add_column("Pipeline Stage", style="cyan", width=30)
    table.add_column("Component / Engine", style="yellow", width=25)
    table.add_column("Latency (ms)", justify="right", style="white")
    table.add_column("Latency (s)", justify="right", style="white")

    table.add_row("1. Button Trigger", "SimulatedGlassesDevice", f"{btn_latency_ms:.2f}", f"{btn_latency_ms/1000.0:.3f}")
    table.add_row("2. Audio Record & STT", "Laptop Mic + Faster-Whisper", f"{stt_duration_ms:.2f}", f"{stt_duration_ms/1000.0:.3f}")
    table.add_row("3. Context Engine", "Temporal & Location Rules", f"{ctx_latency_ms:.2f}", f"{ctx_latency_ms/1000.0:.3f}")
    table.add_row("4. LangGraph + 5. Gemini", f"Gemini ({settings.LLM_MODEL})", f"{gemini_latency_ms:.2f}", f"{gemini_latency_ms/1000.0:.3f}")
    table.add_row("6. Speech Playback (TTS)", "Windows SAPI5", f"{tts_duration_ms:.2f}", f"{tts_duration_ms/1000.0:.3f}")
    table.add_section()
    table.add_row("[bold]TOTAL PIPELINE ROUNDTRIP[/bold]", "[bold]Full End-to-End[/bold]", f"[bold]{overall_total_ms:.2f}[/bold]", f"[bold]{overall_total_ms/1000.0:.3f}[/bold]")

    console.print("\n")
    console.print(table)
    console.print("\n[bold green][OK] Live Gemini Pipeline Test Completed Successfully![/bold green]\n")

if __name__ == "__main__":
    asyncio.run(run_live_pipeline())
