from openai import OpenAI, ChatCompletion
import json
import os
import tools


class Agent:
    def __init__(self, base_url):
        print("Initializing Agent...")
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url=base_url)
        self._messages = [{"role": "system", "content": "Now is Feb 2026"}]
        self._last_response: ChatCompletion = None
        self.wait_prompt = True

    def model_request(self):
        print("Thinking...")
        response = self._client.chat.completions.create(
            model="deepseek-chat",
            messages=self._messages,
            tools=tools.tool_list,
            stream=False,
            max_tokens=800
        )
        self._messages.append(response.choices[0].message.model_dump())
        self._last_response = response

    def send_message(self, message: str) -> str:
        self._messages.append({"role": "user", "content": message})
        self.model_request()
        calls = self._last_response.choices[0].message.tool_calls
        if calls:
            self.wait_prompt = False

        return self._last_response.choices[0].message.model_dump()["content"]

    def get_messages(self):
        message_list = ''
        for message in self._messages:
            message_list += "\n\n >> " + str(message)
        return message_list

    def _use_tool(self, tool) -> str:
        func = tool.function
        print("Using tool '", func.name, "' ...")
        result = tools.tool_functions[func.name](**json.loads(func.arguments))
        return result

    def using_tools(self):
        self.wait_prompt = True
        if self._last_response:
            calls = self._last_response.choices[0].message.tool_calls
            if calls:
                self.wait_prompt = False
                result = self._use_tool(calls[0])
                self._messages.append({
                    "tool_call_id": calls[0].id,
                    "role": "tool",
                    "name": calls[0].function.name,
                    "content": result
                })
                self.model_request()

        return self._last_response.choices[0].message.model_dump()["content"]

