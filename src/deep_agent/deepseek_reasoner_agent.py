from openai import OpenAI, ChatCompletion
import json
import os
import tools
import time
from datetime import datetime
from rich import print as rprint
import tg_funcs

from deepseek_agent import ContextPool, construct_history

LLM_MAX_OUTPUT_TOKENS = 10000

class Agent:
    """
    Reasoning agent using deepseek-v4-pro with thinking mode enabled.
    Properly handles reasoning_content and tool_calls according to DeepSeek spec.
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

        # Use the correct model with thinking mode enabled
        model_name = "deepseek-v4-pro"
        reasoning_effort = "high"

        extra_body = {
            "thinking": {"type": "enabled"},
            "reasoning_effort": reasoning_effort,
            "user_id": f"mastermind_{self.name.lower()}"
        }

        # Build full message list for debugging
        full_messages = [self._system_prompt] + construct_history(self._base_prompts) + self.messages.get_messages()
        # Optional: print the last few messages to verify structure
        print("=== Last 2 messages before API call ===")
        for m in full_messages[-2:]:
            print(f"role={m.get('role')}, has_tool_calls={bool(m.get('tool_calls'))}, content={m.get('content')!r:.50}")

        try:
            response = self._client.chat.completions.create(
                model=model_name,
                messages=full_messages,
                tools=tools.tool_list if self._use_tools else [],
                stream=False,
                max_tokens=LLM_MAX_OUTPUT_TOKENS,
                extra_body=extra_body
            )
            return response
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code >= 500:
                print(f"DeepSeek server error: {e}. Retrying in 2 seconds...")
                time.sleep(2)
                return self.llm_request()
            raise


    def run(self, initial_user_request='', chat_id=None):
        while True:
            llm_response = self.llm_request()
            llm_response_message = llm_response.choices[0].message.model_dump()

            has_tool_calls = bool(llm_response.choices[0].message.tool_calls)

            if has_tool_calls:
                print(f"DEBUG: Assistant response with {len(llm_response.choices[0].message.tool_calls)} tool_calls")

            # Append assistant message (method sets content=None if tool_calls present)
            self.messages.append_assistant_message(llm_response_message, self._save_history, has_tool_calls)

            rprint(self.messages.get_chat_history([llm_response_message]))

            calls = llm_response.choices[0].message.tool_calls
            if calls:
                # Show internal thought (reasoning + content) to user
                if self.tgbot:
                    reasoning = llm_response_message.get("reasoning_content", "")
                    content = llm_response_message.get("content", "")
                    if reasoning or content:
                        tg_message = f"[{reasoning}]\n\n{content}" if reasoning else content
                        self.tgbot.internal_thought(tg_message)

                # Execute ALL tool calls and append responses
                for tool_call in calls:
                    result = self._use_tool(tool_call, initial_user_request)
                    tool_response_msg = {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": result,
                    }
                    self.messages.append(tool_response_msg, False)
                # Continue loop to send all tool responses back to the model
            else:
                # Final answer (no tool calls)
                if self.tgbot:
                    reasoning = llm_response_message.get("reasoning_content", "")
                    content = llm_response_message.get("content", "")
                    if reasoning or content:
                        tg_message = f"[{reasoning}]\n\n{content}" if reasoning else content
                        if chat_id:
                            self.tgbot.reply(tg_message, chat_id)
                        else:
                            self.tgbot.send_message(tg_message)
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

