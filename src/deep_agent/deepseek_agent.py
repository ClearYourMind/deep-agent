from openai import OpenAI, ChatCompletion
import json
import os
import tools
from datetime import datetime
from rich import print as rprint
import tg_funcs

LLM_MAX_OUTPUT_TOKENS = 2000

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
        self._max_length = 48000
        self.overflow = False
        self.last_memory = last_memory

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
            chat += f"\n**{message['role']}:** [{message.get('time', '--.--.-- --:--:--')}]\n"
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
            helper_response_content = helper_response.choices[0].message.content

            with open('compressed_history.txt', 'a', encoding='utf-8') as f:
                f.write("# **Regular compression**:\n")
                f.write(helper_response_content + "\n\n")
            with open('last_compression.txt', 'w', encoding='utf-8') as f:
                f.write(helper_response_content + "\n\n")

            self.assign_messages(self._compressed_history + construct_history(self.last_memory))
            self._compressed_history.append(helper_response.choices[0].message.model_dump()) # append after reconstructing to avoid duplication of last compressed context
            print("\n\nCompressed context:\n", self.get_chat_history(self._compressed_history), "\n\n")
            self.overflow = False


class Agent:
    def __init__(self, name, base_url="https://api.deepseek.com/beta", system_prompt="", base_prompts="", last_memory="",  use_tools=True, save_history=True, tgbot=None):
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

        #       add helper_agent into function arguments
        if self._helper_agent:
            args["helper_agent"] = self._helper_agent
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
            self.tgbot.internal_thought("Обдумываю дальнейшие действия...")

        return self._client.chat.completions.create(
            model="deepseek-chat",
            messages = [self._system_prompt] + construct_history(self._base_prompts) + self.messages.get_messages(),
            tools=tools.tool_list if self._use_tools else [],
            stream=False,
            max_tokens=LLM_MAX_OUTPUT_TOKENS,
            temperature=1.3

        )


    def run(self, initial_user_request='', chat_id=None):
        while True:
            llm_response = self.llm_request()
            llm_response_message = llm_response.choices[0].message.model_dump()
            self.messages.append(llm_response_message, self._save_history)
            rprint(self.messages.get_chat_history([llm_response_message]))

            calls = llm_response.choices[0].message.tool_calls
            if calls:
                if self.tgbot:
                    if llm_response_message["content"]:
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
                        self.tgbot.reply(llm_response_message["content"], chat_id)
                    else:
                        if llm_response_message["content"]:
                            self.tgbot.send_message(llm_response_message["content"])
                break

        self.tgbot.internal_thought("Готово!")
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
