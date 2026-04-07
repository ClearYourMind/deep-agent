from openai import OpenAI, ChatCompletion
import json
import os
import tools
from datetime import datetime
from rich import print as rprint

LLM_MAX_TOKENS = 2000


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
        message["time"] = datetime.now().strftime("%d.%m.%Y, %H:%M")
        self._messages.append(message)
        if save_history:
            with open('message_history.md', 'a', encoding='utf-8') as f:
                f.write(f"**{message['role']}:** [{message['time']}]\n")
                f.write(f"{message['content']}\n---\n\n")

        if self.get_context_length() > self._max_length:
            print("\t !!! Context max length overflow. It should be compressed !!!")
            self.overflow = True
        else:
            self.overflow = False


    def get_messages(self):
        result = self._messages[:]
        return result


    def get_chat_history(self, messages=None):
        chat = ''
        if not messages:
            messages = self._messages

        for message in messages:
            chat += f"\n**{message['role']}:** [{message['time']}]\n"
            chat += f"{message['content']}\n---\n"
        return chat


    def assign_messages(self, messages):
        self._messages = messages[:]


    def extensive_compression(self, helper_agent):
            # compress compressed history
        print('\n\n ..Extensive history compression..')
        helper_message = {'role': 'user', 'name': 'MASTERMIND', 'content':
            "**ACTION**: COMPRESS\n\n**CONTENT**:\n" + self.get_chat_history(self._compressed_history)
        }
        helper_agent.messages.assign_messages([helper_message])
        helper_response = helper_agent.llm_request()
        print("\nExtensively compressed history:\n", helper_response.choices[0].message.content)
        self._compressed_history = [helper_response.choices[0].message.model_dump()]

        with open('compressed_history.txt', 'a', encoding='utf-8') as f:
            f.write("# **Extensive compression**:\n")
            f.write(helper_response.choices[0].message.content + "\n\n")


    def compress_context(self, helper_agent):
        if helper_agent:
            if len(self._compressed_history) > 20:
                self.extensive_compression(helper_agent)

            print('\n\n ..Context compression started..')
            helper_message = {'role': 'user', 'name': 'MASTERMIND', 'content':
                "**ACTION**: COMPRESS\n\n**CONTENT**:\n" + self.get_chat_history()
            }
            helper_agent.messages.assign_messages([helper_message])
            helper_response = helper_agent.llm_request()

            self._compressed_history.append(helper_response.choices[0].message.model_dump())
            print("\n\nCompressed context:\n", self.get_chat_history(self._compressed_history), "\n\n")

            with open('compressed_history.txt', 'a', encoding='utf-8') as f:
                f.write("# **Regular compression**:\n")
                f.write(helper_response.choices[0].message.content + "\n\n")
            with open('last_compression.txt', 'w') as f:
                f.write(helper_response.choices[0].message.content)

            self.assign_messages(self._compressed_history)
            self.overflow = False


class Agent:
    def __init__(self, name, base_url="https://api.deepseek.com/beta", system_prompt="", use_tools=True, save_history=True):
        print("Initializing agent", name, "...")
        self.name = name
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_'+self.name), base_url=base_url)
        self._system_prompt = {"role": "system", "name": "Creator", "content": system_prompt}
        self._extended_system_prompt = None
        self._use_tools = use_tools
        self.messages = ContextPool()
        self._helper_agent = None
        self._save_history = save_history


    def add_helper_agent(self, helper_agent):
        self._helper_agent = helper_agent


    def set_extended_system_prompt(self, prompt_messages):
        self._extended_system_prompt = prompt_messages


    def _use_tool(self, tool, user_request) -> str:
        func = tool.function
        print(self.name + " Using tool '" + func.name + "' ...")
        try:
            args = json.loads(tool.function.arguments)
        except json.decoder.JSONDecodeError as e:
            print("\n\nEncountered JSONDecodeError during parsing arguments")
            with open('last_error.log', 'w', encoding='utf-8') as f:
                f.write(str(e)+'\n')
                f.write(tool.function.arguments)
            return "Output truncated. Maybe it is too long. Remember about token limitation."

        #       add helper_agent into function arguments
        if self._helper_agent:
            args["helper_agent"] = self._helper_agent
            args["user_request"] = user_request

        result = tools.tool_functions[func.name](**args)
        return result

    
    def llm_request(self):
        print(self.name + " Messages count:", self.messages.get_messages_count(), " Context length:", self.messages.get_context_length())
        print(self.name + " Thinking...")
        return self._client.chat.completions.create(
            model="deepseek-chat",
            messages = [self._system_prompt] + (self._extended_system_prompt if self._extended_system_prompt else []) + self.messages.get_messages(),
            tools=tools.tool_list if self._use_tools else [],
            stream=False,
            max_tokens=LLM_MAX_TOKENS
        )


    def run(self, user_request):
        while True:
            llm_response = self.llm_request()
            self.messages.append(llm_response.choices[0].message.model_dump(), self._save_history)
            rprint(self.messages.get_chat_history(self.messages.get_messages()[-1:]))

            calls = llm_response.choices[0].message.tool_calls
            if calls:
                result = self._use_tool(calls[0], user_request)
                self.messages.append({
                    "tool_call_id": calls[0].id,
                    "role": "tool",
                    "name": calls[0].function.name,
                    "content": result
                }, False)
            else:
                break

        #       task complete. Tool-calling loop ended
        if self._save_history:
            with open('message_history.md', 'a', encoding='utf-8') as f:
                f.write("\n---\n\n")
            with open('last_completed_task.md', 'w', encoding='utf-8') as f:
                f.write(llm_response.choices[0].message.content + "\n---\n\n")
            with open('completed_tasks_history.md', 'a', encoding='utf-8') as f:
                f.write(llm_response.choices[0].message.content + "\n---\n\n")

        if self.messages.overflow:
            self.messages.compress_context(self._helper_agent)
