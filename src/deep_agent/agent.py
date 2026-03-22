from openai import OpenAI, ChatCompletion
import json
import os

max_content_length_truncate = 1000


class ContextPool:
    def __init__(self, init_message):
        self._messages = [init_message]
        self._important_messages = [init_message]
        self._max_length = 10000
        self.overflow = False

    def get_context_length(self):
        result_length = 0
        for msg in self._messages:
            result_length += len(msg["content"])
        return result_length

    def get_messages_count(self):
        return len(self._messages)

    def append(self, message):
        self._messages.append(message)
        if self.get_context_length() > self._max_length:
            self.compress_context_hard()
            self.overflow = True
        else:
            self.overflow = False

    def compress_context_hard(self):
        print("\t !!! Context max length overflow. It should be compressed !!!")
        for msg in self._messages:
            if msg["role"] == "tool":
                msg["content"] = ""
            else:
                msg["content"] = (msg["content"][:max_content_length_truncate])
        self.overflow = False

    def get_messages(self):
        result = self._messages[:]
        return result

    def update_important_messages(self, clear_history=False):
        msg = self._messages[-2]
        if (msg["role"] == "tool") and (msg["name"] == "complete"):
            self._important_messages.append(self._messages[-1])
            if clear_history:
                self._messages = self._important_messages[:]
                self.overflow = False


import tools

class Agent:
    def __init__(self, base_url):
        print("Initializing Agent...")
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url=base_url)
        self._messages = ContextPool({"role": "system", "content":
            """
                You are run inside a python-script as interactive agent.
                Main intention is to achieve minimal token cost while maintaining full message history context as much as possible
            """
        })
        self._last_response: ChatCompletion = None
        self.wait_prompt = True

    def model_request(self):
        print("Messages count:", self._messages.get_messages_count(), " Context length:", self._messages.get_context_length())
        print("Thinking...")
        response = self._client.chat.completions.create(
            model="deepseek-chat",
            messages=self._messages.get_messages(),
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

        #return self._last_response.choices[0].message.content

    def get_messages(self):
        message_list = ''
        for message in self._messages:
            message_list += "\n\n >> " + str(message)
        return message_list

    def _use_tool(self, tool) -> str:
        func = tool.function
        print("Using tool '" + func.name + "' ...")
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
            else: 
                self._messages.update_important_messages(clear_history=True)
                print("\n\n")
                print("Message history:\n")
                print(self._messages.get_messages())
                print("\n\n")

        return self._last_response.choices[0].message.content

