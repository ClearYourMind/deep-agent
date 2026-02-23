from openai import OpenAI
import json
import os


class Agent:
    def __init__(self, base_url):
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url=base_url)
        self._messages = [{"role": "system", "content": "You are a helpful assistant"}]

    def send_message(self, message: str) -> str:
        self._messages.append({"role": "user", "content": message})

        response = self._client.chat.completions.create(
            model="deepseek-chat",
            messages=self._messages,
            stream=False,
            max_tokens=200
        )
        self._messages.append(response.choices[0].message.to_dict())
        return response.choices[0].message.content

    def get_messages(self):
        return str(self._messages)



