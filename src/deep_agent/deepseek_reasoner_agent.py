from openai import OpenAI, ChatCompletion
import json
import os
import tools
from datetime import datetime
from rich import print as rprint
import tg_funcs

from deepseek_agent import ContextPool, construct_history

LLM_MAX_OUTPUT_TOKENS = 3000

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

        return self._client.chat.completions.create(
            model="deepseek-reasoner",
            messages = [self._system_prompt] + construct_history(self._base_prompts) + self.messages.get_messages(),
            tools=tools.tool_list if self._use_tools else [],
            stream=False,
            max_tokens=LLM_MAX_OUTPUT_TOKENS,
            temperature=1.3,
            extra_body={"thinking":{"type": "enabled"}}
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
                    if llm_response_message.get("content", "") or llm_response_message.get("reasoning_content", ""):
                        tg_message = f"[{llm_response_message.get("reasoning_content", "")}]\n\n{llm_response_message.get("content", "")}"
                        self.tgbot.internal_thought(tg_message)

                result = self._use_tool(calls[0], initial_user_request)
                self.messages.append({
                    "tool_call_id": calls[0].id,
                    "role": "tool",
                    "name": calls[0].function.name,
                    "content": result,
                }, False)
            else:
                if self.tgbot:
                    if llm_response_message.get("content", "") or llm_response_message.get("reasoning_content", ""):
                        tg_message = f"[{llm_response_message.get("reasoning_content", "")}]\n\n{llm_response_message.get("content", "")}"
                        self.tgbot.internal_thought(tg_message)
                # clear_reasoning_content()
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
