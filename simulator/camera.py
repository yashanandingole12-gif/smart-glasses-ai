import base64
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("SmartGlasses.Camera")

class SimulatorCamera:
    def __init__(self, capture_dir: Optional[str] = None):
        self.capture_dir = Path(capture_dir or "captures").resolve()
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    def capture_image(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Captures a single frame from webcam.
        Returns: (success, image_path, base64_str)
        """
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.warning("No webcam detected. Creating a simulated test frame.")
                return self._create_simulated_frame()

            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.warning("Could not read frame from webcam. Using simulated test frame.")
                return self._create_simulated_frame()

            filepath = self.capture_dir / "latest_snapshot.jpg"
            cv2.imwrite(str(filepath), frame)

            _, buffer = cv2.imencode('.jpg', frame)
            b64_str = base64.b64encode(buffer).decode('utf-8')
            return True, str(filepath), b64_str

        except Exception as ex:
            logger.error(f"Webcam capture error ({ex}). Using simulated frame.")
            return self._create_simulated_frame()

    def _create_simulated_frame(self) -> Tuple[bool, str, str]:
        # Minimal 1x1 jpeg placeholder or test pattern
        filepath = self.capture_dir / "simulated_snapshot.jpg"
        dummy_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
        filepath.write_bytes(dummy_bytes)
        b64_str = base64.b64encode(dummy_bytes).decode('utf-8')
        return True, str(filepath), b64_str
