import requests

OLLAMA_URL = "http://ai-ollama:11434/api/generate"
MODEL = "llama3.2:1b"


class AIService:

    @staticmethod
    def generate(prompt: str) -> str:

        try:

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "No response returned.")

        except Exception as e:

            return f"AI Error : {str(e)}"