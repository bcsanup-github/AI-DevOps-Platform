import requests

from app.config import OLLAMA_HOST, OLLAMA_MODEL


class AIService:

    @staticmethod
    def generate(prompt: str) -> str:

        try:

            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300
            )

            if response.status_code == 404:
                return (
                    f"Model '{OLLAMA_MODEL}' is not installed in Ollama. "
                    f"Run: docker exec -it ai-ollama ollama pull {OLLAMA_MODEL}"
                )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "No response returned.")

        except requests.RequestException as e:

            return f"AI Error : {str(e)}"
