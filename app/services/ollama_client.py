import requests
import json

class OllamaClient:
    def __init__(self, host="http://127.0.0.1:11434", model="llama3"):
        self.host = host
        self.model = model

    def generate(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {"model": self.model, "prompt": prompt}
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
            response.raise_for_status()

            text = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    text += chunk.get("response", "")
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
            return text

        except Exception as e:
            print(f"Ошибка генерации: {e}")
            return None
