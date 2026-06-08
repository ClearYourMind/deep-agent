from openai import OpenAI, ChatCompletion
import json
import os
import tools
import time
from datetime import datetime
from rich import print as rprint
import tg_funcs

LLM_MAX_OUTPUT_TOKENS = 10000


def construct_history(prompts_list):
    composed_prompt = []
    for prompt_text, prompt_file in prompts_list:
        prompt_content = prompt_text
        if prompt_file:
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content += f.read()
            except:
                print(f"File {prompt_file} is not loaded")
        prompt_content += "\n\n---\n\n"
        composed_prompt.append({'role': 'user', 'name': 'MASTERMIND', 'content': prompt_content})
    return composed_prompt


class ContextPool:
    def __init__(self, last_memory=""):
        self._messages = []
        self._compressed_history = []
        self._max_length = 96000
        self.overflow = False
        self.last_memory = last_memory


    def get_context_length(self):
        result_length = 0
        for msg in self._messages:
            result_length += len(msg.get("content") or "")
        return result_length


    def get_messages_count(self):
        return len(self._messages)


    def append(self, message, save_history):
        """Legacy append – use append_assistant_message for assistant replies."""
        message["time"] = datetime.now().strftime("%d.%m.%Y, %H:%M")
        self._messages.append(message)
        if save_history:
            with open('message_history.md', 'a', encoding='utf-8') as f:
                f.write(f"**{message['role']}:** [{message['time']}]\n")
                if message.get('reasoning_content'):
                    f.write(f"*Reasoning:* {message['reasoning_content']}\n\n")
                f.write(f"{message.get('content', '')}\n---\n\n")
        if self.get_context_length() > self._max_length:
            print("\t !!! Context max length overflow. It should be compressed !!!")
            self.overflow = True
        else:
            self.overflow = False


    def append_assistant_message(self, message, save_history, has_tool_calls=False):
        """
        Append an assistant message, correctly handling reasoning_content and content.
        According to DeepSeek/OpenAI spec:
        - If tool_calls present, content MUST be None (or empty)
        - reasoning_content is allowed only when thinking mode is enabled
        """
        msg_copy = message.copy()
        msg_copy["time"] = datetime.now().strftime("%d.%m.%Y, %H:%M")

        # CRITICAL: When there are tool_calls, content must be None
        if has_tool_calls:
            msg_copy["content"] = None
            # Keep reasoning_content as is (required for follow-up calls)
            # Keep tool_calls array
        else:
            # No tool_calls: discard reasoning_content (API ignores it)
            msg_copy.pop('reasoning_content', None)
            # Ensure content is a string; if None, set empty string
            if msg_copy.get("content") is None:
                msg_copy["content"] = ""

        # Remove any empty content fields to avoid confusion (but for tool_calls we already set None)
        if not has_tool_calls and msg_copy.get('content') == '':
            pass  # keep as empty string

        self._messages.append(msg_copy)

        if save_history:
            with open('message_history.md', 'a', encoding='utf-8') as f:
                f.write(f"**{msg_copy['role']}:** [{msg_copy['time']}]\n")
                if msg_copy.get('reasoning_content'):
                    f.write(f"*Reasoning:* {msg_copy['reasoning_content']}\n\n")
                f.write(f"{msg_copy.get('content', '')}\n---\n\n")

        if self.get_context_length() > self._max_length:
            print("\t !!! Context max length overflow. It should be compressed !!!")
            self.overflow = True
        else:
            self.overflow = False


    def get_messages(self):
        return self._messages[:]


    def get_chat_history(self, messages=None):
        chat = ''
        if not messages:
            messages = self._messages
        for message in messages:
            chat += f"\n**{message['role']}:** [{message.get('time', '--.--.-- --:--:--')}]\n"
            if message.get('reasoning_content'):
                chat += f"*reasoning:* {message['reasoning_content']}\n\n"
            chat += f"{message.get('content', '')}\n---\n"
        return chat


    def assign_messages(self, messages):
        self._messages = messages[:]


    def extensive_compression(self, helper_agent):
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
            helper_response_content = helper_response.choices[0].message.content

            with open('compressed_history.txt', 'a', encoding='utf-8') as f:
                f.write("# **Regular compression**:\n")
                f.write(helper_response_content + "\n\n")
            with open('last_compression.txt', 'w', encoding='utf-8') as f:
                f.write(helper_response_content + "\n\n")

            self.assign_messages(self._compressed_history + construct_history(self.last_memory))
            self._compressed_history.append(helper_response.choices[0].message.model_dump())
            print("\n\nCompressed context:\n", self.get_chat_history(self._compressed_history), "\n\n")
            self.overflow = False


class Agent:
    """
    Standard agent using deepseek-v4-flash (non‑thinking mode, faster).
    """
    def __init__(self, name, base_url="https://api.deepseek.com/", system_prompt="", base_prompts="", last_memory="", use_tools=True, save_history=True, tgbot=None):
        print("Initializing agent", name, "... ", end='')
        self.name = name
        self._client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_'+self.name), base_url=base_url)
        self._system_prompt = {"role": "system", "name": "Creator", "content": system_prompt}
        self._base_prompts = base_prompts
        self._use_tools = use_tools
        self.messages = ContextPool(last_memory)
        self._helper_agent = None
        self._save_history = save_history
        self.tgbot = tgbot
        if last_memory:
            self.messages.assign_messages(construct_history(last_memory))
        print("Done")


    def add_helper_agent(self, helper_agent):
        self._helper_agent = helper_agent


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

        if self._helper_agent:
            args["helper_agent"] = self._helper_agent
            args["tg_bot"] = self.tgbot
            args["user_request"] = user_request

        thought = f"tool: {func.name}\n"+ '\n'.join([f"{arg} = {value}" for arg, value in args.items()])
        if self.tgbot:
            self.tgbot.internal_thought(thought)
        print(thought)
        result = tools.tool_functions[func.name](**args)
        if self.tgbot:
           self.tgbot.internal_thought(f"result: {result}")
        return result


    def llm_request(self):
        print(self.name + " Messages count:", self.messages.get_messages_count(), " Context length:", self.messages.get_context_length())
        print(self.name + " Thinking...")
        if self.tgbot:
            self.tgbot.internal_thought("Обдумываю ответ...")

        # New model: deepseek-v4-flash (faster, non‑thinking)
        model_name = "deepseek-v4-flash"
        extra_body = {
            "user_id": f"mastermind_{self.name.lower()}"
        }

        return self._client.chat.completions.create(
            model=model_name,
            messages=[self._system_prompt] + construct_history(self._base_prompts) + self.messages.get_messages(),
            tools=tools.tool_list if self._use_tools else [],
            stream=False,
            max_tokens=LLM_MAX_OUTPUT_TOKENS,
            temperature=1.3,
            extra_body=extra_body
        )


    def run(self, initial_user_request='', chat_id=None):
        while True:
            llm_response = self.llm_request()
            llm_response_message = llm_response.choices[0].message.model_dump()

            has_tool_calls = bool(llm_response.choices[0].message.tool_calls)
            self.messages.append_assistant_message(llm_response_message, self._save_history, has_tool_calls)

            rprint(self.messages.get_chat_history([llm_response_message]))

            calls = llm_response.choices[0].message.tool_calls
            if calls:
                if self.tgbot:
                    if llm_response_message.get("content"):
                        if chat_id:
                            self.tgbot.reply(llm_response_message["content"], chat_id)
                        else:
                            self.tgbot.internal_thought(llm_response_message["content"])

                result = self._use_tool(calls[0], initial_user_request)
                self.messages.append({
                    "tool_call_id": calls[0].id,
                    "role": "tool",
                    "name": calls[0].function.name,
                    "content": result
                }, False)
            else:
                if self.tgbot:
                    if chat_id:
                        if llm_response_message.get("content"):
                            self.tgbot.reply(llm_response_message["content"], chat_id)
                    else:
                        if llm_response_message.get("content"):
                            self.tgbot.send_message(llm_response_message["content"])
                break

        self.tgbot.internal_thought("Готово!")

        if self._save_history:
            with open('message_history.md', 'a', encoding='utf-8') as f:
                f.write("\n---\n\n")
            with open('last_completed_task.md', 'w', encoding='utf-8') as f:
                f.write(llm_response.choices[0].message.content + "\n---\n\n")
            with open('completed_tasks_history.md', 'a', encoding='utf-8') as f:
                f.write(llm_response.choices[0].message.content + "\n---\n\n")

        if self.messages.overflow:
            self.messages.compress_context(self._helper_agent)

