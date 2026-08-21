import sys
import asyncio
from typing import Callable, Optional

class KeyboardHandler:
    """
    Handles terminal keyboard commands for simulated smart glasses button presses.
    Supports ENTER / SPACE for push-to-talk, C for camera, B for battery status, Q for quit.
    """
    def __init__(
        self,
        on_button_press: Callable[[], None],
        on_camera_press: Callable[[], None],
        on_battery_press: Callable[[], None],
        on_quit: Callable[[], None],
        on_text_input: Optional[Callable[[str], None]] = None
    ):
        self.on_button_press = on_button_press
        self.on_camera_press = on_camera_press
        self.on_battery_press = on_battery_press
        self.on_quit = on_quit
        self.on_text_input = on_text_input
        self._running = True

    async def run_input_loop(self):
        """Asynchronous standard input loop for cross-platform terminal compatibility."""
        loop = asyncio.get_event_loop()
        while self._running:
            try:
                # Read line from standard input
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    await asyncio.sleep(0.1)
                    continue

                cmd = line.strip()

                if cmd == "" or cmd.lower() == "enter" or cmd.lower() == "talk":
                    self.on_button_press()
                elif cmd.lower() == "c":
                    self.on_camera_press()
                elif cmd.lower() == "b":
                    self.on_battery_press()
                elif cmd.lower() == "q" or cmd.lower() == "quit":
                    self.on_quit()
                    break
                else:
                    # If user typed a custom query directly (e.g. "Good morning"), send it
                    if self.on_text_input:
                        self.on_text_input(cmd)
                    else:
                        self.on_button_press()
            except (KeyboardInterrupt, EOFError):
                self.on_quit()
                break

    def stop(self):
        self._running = False
