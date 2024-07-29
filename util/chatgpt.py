import json
import urllib.request


class ChatGpt:
    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.headers: dict[str, str] = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_response(self, prompt: str) -> str:
        payload: dict[str, str] = {
            "model": "gpt-4o-2024-05-13",
            "seed": 0,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            headers=self.headers,
            data=json.dumps(payload).encode("utf-8"),
        )

        response = json.loads(
            urllib.request.urlopen(request).read().decode("utf-8")
        )
        return response["choices"][0]["message"]["content"]
