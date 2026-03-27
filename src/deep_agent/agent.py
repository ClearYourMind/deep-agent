from openai import OpenAI, ChatCompletion
import json
import os
import tools

# max_content_length_truncate = 1000


class ContextPool:
    def __init__(self):
        self._messages = []
        self._important_messages = []
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
            self.compress_context_midtask()
            self.overflow = True
        else:
            self.overflow = False

    def compress_context_midtask(self):
        print("\t !!! Context max length overflow. It should be compressed !!!")
        ...
        # for msg in self._messages:
        #     if msg["role"] == "tool":
        #         msg["content"] = ""
        # self.overflow = False

    def get_messages(self):
        result = self._messages[:]
        return result

    def assign_messages(self, messages):
        self._messages = messages[:]

    def update_important_messages(self, clear_history=False):
        #       adds last message to important messages
        self._important_messages.append(self._messages[-1])
        if clear_history:
            self._messages = self._important_messages[:]
            self.overflow = False


class Agent:
    def __init__(self, name, base_url="https://api.deepseek.com/beta", system_prompt="", use_tools=True):
        print("Initializing agent", name, "...")
        self.name = name
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_'+self.name), base_url=base_url)
        self._system_prompt = {"role": "system", "content": system_prompt}
        self._messages = ContextPool()
        self.last_response: ChatCompletion = None
        self.wait_prompt = True
        self._helper_agent = None
        self.use_tools = use_tools
        self.last_user_request = ""

    def add_helper_agent(self, helper_agent):
        self._helper_agent = helper_agent

    def model_request(self):
        print(self.name + " Messages count:", self._messages.get_messages_count(), " Context length:", self._messages.get_context_length())
        print(self.name + " Thinking...")
        response = self._client.chat.completions.create(
            model="deepseek-chat",
            messages=[self._system_prompt] + self._messages.get_messages(),
            tools=tools.tool_list if self.use_tools else [],
            stream=False,
            max_tokens=800
        )
        self._messages.append(response.choices[0].message.model_dump())
        self.last_response = response

    def send_message(self, message: str, output=False) -> str:
        self._messages.append({"role": "user", "content": message})
        self.last_user_request = message
        self.model_request()
        calls = self.last_response.choices[0].message.tool_calls
        if calls:
            self.wait_prompt = False

        return self.last_response.choices[0].message.content if output else None

    def get_messages(self):
        message_list = ''
        for message in self._messages.get_messages():
            message_list += "\n\n >> " + message["role"] + ": " + message["content"]
        return message_list

    def clear_message_history(self):
        self._messages.assign_messages([])

    def _use_tool(self, tool) -> str:
        func = tool.function
        print(self.name + " Using tool '" + func.name + "' ...")
        args = json.loads(tool.function.arguments)
        #       add helper_agent into function arguments
        if self._helper_agent:
            args["helper_agent"] = self._helper_agent
            args["user_request"] = self.last_user_request

        result = tools.tool_functions[func.name](**args)
        return result

    def using_tools(self):
        self.wait_prompt = True
        if self.last_response:
            calls = self.last_response.choices[0].message.tool_calls
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
                # task complete. End of tool-calling loop
                #self._messages.update_important_messages(clear_history=True)
                print("\n\n")
                print(self.name, " Message history:\n")
                print(self.get_messages())
                print("\n\n")

        return self.last_response.choices[0].message.content

