from models.base_model import BaseModel
from PIL import Image
import base64
import json
import os
import urllib.request
from io import BytesIO
from typing import Dict


class OllamaVisionModel(BaseModel):
    def __init__(
        self,
        model_name: str = "llava",
        endpoint: str = None,
        user_prompt: str = None,
        timeout: int = None,
        max_image_size: int = 1024,
    ):
        self.model_name = model_name
        self.endpoint = endpoint or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
        self.user_prompt = user_prompt or ""
        self.timeout = int(timeout or os.getenv("OLLAMA_TIMEOUT", "900"))
        self.max_image_size = max_image_size

    @property
    def name(self) -> str:
        return f"ollama-{self.model_name}"

    def resize_image(self, image: Image.Image) -> Image.Image:
        if self.max_image_size <= 0:
            return image.convert("RGB")

        width, height = image.size
        if width <= self.max_image_size and height <= self.max_image_size:
            return image.convert("RGB")

        if width > height:
            new_width = self.max_image_size
            new_height = int(height * (self.max_image_size / width))
        else:
            new_height = self.max_image_size
            new_width = int(width * (self.max_image_size / height))

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS).convert("RGB")

    def image_to_base64(self, image: Image.Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def predict(self, input_data: Dict) -> str:
        try:
            return self._predict_image_text(input_data)
        except Exception as exc:
            return f"Error in Ollama prediction: {exc}"

    def _predict_image_text(self, input_data: Dict) -> str:
        image = Image.open(input_data["image_path"])
        image_b64 = self.image_to_base64(self.resize_image(image))

        prompt = (
            f"{input_data['text']}\n\n"
            f"{self.user_prompt}\n\n"
            "Answer with only one final option: A, B, C, or D."
        )

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }

        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data.get("response", "")
