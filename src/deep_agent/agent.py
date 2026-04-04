from openai import OpenAI, ChatCompletion
import json
import os
import tools

class ContextPool:
    def __init__(self):
        self._messages = []
        self._compressed_history = []
        self._max_length = 20000
        self.overflow = False

    def get_context_length(self):
        result_length = 0
        for msg in self._messages:
            result_length += len(msg["content"])
        return result_length

    def get_messages_count(self):
        return len(self._messages)

    def append(self, message, save_history):
        self._messages.append(message)
        if save_history:
            with open('message_history.md', 'a') as f:
                f.write(f">> {message['role']}:\n{message['content']}\n\n")

        if self.get_context_length() > self._max_length:
            print("\t !!! Context max length overflow. It should be compressed !!!")
            self.overflow = True
        else:
            self.overflow = False

    def get_messages(self):
        result = self._messages[:]
        return result

    def get_chat_history(self, messages=None):
        message_list = ''
        if not messages:
            messages = self._messages

        for message in messages:
            message_list += " >> " + message["role"] + ": " + message["content"] + "\n\n"
        return message_list

    def assign_messages(self, messages):
        self._messages = messages[:]

    def extensive_compression(self, helper_agent):
            # compress compressed history
        print('\n\n ..Extensive history compression..')
        helper_message = """
**ACTION**: COMPRESS

**CONTENT**:
"""
        helper_message += self.get_chat_history(self._compressed_history)
        result = helper_agent.send_message(helper_message, output=True)
        print("\nExtensively compressed history:\n", result)
        self._compressed_history = [{"role": "system", "name": "COMPRESSOR", "content": result}]

        with open('compressed_history.txt', 'a') as f:
            f.write("# **Extensive compression**:\n")
            f.write(result + "\n\n")

    def compress_context(self, helper_agent):
        if helper_agent:
            if len(self._compressed_history) > 20:
                self.extensive_compression(helper_agent)

            print('\n\n ..Context compression started..')
            helper_message = """
**ACTION**: COMPRESS

**CONTENT**:
"""
            helper_message += self.get_chat_history(self._messages)
            result = helper_agent.send_message(helper_message, output=True)
            print("\nCompressed context:\n", result)
            self._compressed_history.append({"role": "system", "name": "COMPRESSOR", "content": result})

            with open('compressed_history.txt', 'a') as f:
                f.write("# **Regular compression**:\n")
                f.write(result + "\n\n")

            self.assign_messages(self._compressed_history)
            self.overflow = False

class Agent:
    def __init__(self, name, base_url="https://api.deepseek.com/beta", system_prompt="", use_tools=True, save_history=True):
        print("Initializing agent", name, "...")
        self.name = name
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_'+self.name), base_url=base_url)
        self._system_prompt = {"role": "system", "name": "Creator", "content": system_prompt}
        self._extended_system_prompt = None
        self.messages = ContextPool()
        self.last_response: ChatCompletion = None
        self.wait_prompt = True
        self._helper_agent = None
        self.use_tools = use_tools
        self._save_history = save_history
        self.last_user_request = ""

    def add_helper_agent(self, helper_agent):
        self._helper_agent = helper_agent

    def model_request(self):
        print(self.name + " Messages count:", self.messages.get_messages_count(), " Context length:", self.messages.get_context_length())
        print(self.name + " Thinking...")
        response = self._client.chat.completions.create(
            model="deepseek-chat",
            messages = [self._system_prompt] + (self._extended_system_prompt if self._extended_system_prompt else []) + self.messages.get_messages(),
            tools=tools.tool_list if self.use_tools else [],
            stream=False,
            max_tokens=2000
        )
        self.messages.append(response.choices[0].message.model_dump(), self._save_history)
        self.last_response = response

    def send_message(self, message: str, output=False) -> str:
        self.messages.append({"role": "user", "content": message}, self._save_history)
        self.last_user_request = message
        self.model_request()
        calls = self.last_response.choices[0].message.tool_calls
        if calls:
            self.wait_prompt = False

        return self.last_response.choices[0].message.content if output else None

    def clear_message_history(self):
        self.messages.assign_messages([])

    def set_extended_system_prompt(self, prompt_messages):
        self._extended_system_prompt = prompt_messages

    def _use_tool(self, tool) -> str:
        func = tool.function
        is_argument_parsing_success = True
        print(self.name + " Using tool '" + func.name + "' ...")
        try:
            args = json.loads(tool.function.arguments)
        except json.decoder.JSONDecodeError as e:
            is_argument_parsing_success = False
            print("\n\nEncountered JSONDecodeError during parsing arguments")
            with open('last_error.log', 'w') as f:
                f.write(str(e)+'\n')
                f.write(tool.function.arguments)

        if is_argument_parsing_success:
            #       add helper_agent into function arguments
            if self._helper_agent:
                args["helper_agent"] = self._helper_agent
                args["user_request"] = self.last_user_request
            result = tools.tool_functions[func.name](**args)
        else:
            result = "Encountered JSONDecodeError during parsing arguments. Erroneous argument. Maybe it is too long. Please remember about token limitation."

        return result

    def using_tools(self):
        self.wait_prompt = True
        if self.last_response:
            calls = self.last_response.choices[0].message.tool_calls
            if calls:
                self.wait_prompt = False
                result = self._use_tool(calls[0])
                self.messages.append({
                    "tool_call_id": calls[0].id,
                    "role": "tool",
                    "name": calls[0].function.name,
                    "content": result
                }, self._save_history)
                self.model_request()
            else: 
                #       task complete. End of tool-calling loop
                if self._save_history:
                    with open('message_history.md', 'a') as f:
                        f.write("\n----------\n\n")
                    with open('completed_tasks_history.md', 'a') as f:
                        f.write(self.last_response.choices[0].message.content + "\n\n")

                if self.messages.overflow:
                    self.messages.compress_context(self._helper_agent)
                    self.messages.append({"role": "assistant", "content": self.last_response.choices[0].message.content}, self._save_history)

        return self.last_response.choices[0].message.content

