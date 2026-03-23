from openai import OpenAI, ChatCompletion
import json
import os

# max_content_length_truncate = 1000


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
        self.overflow = False

    def get_messages(self):
        result = self._messages[:]
        return result

    def update_important_messages(self, clear_history=False):
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
**VALUES**
- Keep conversation context concise and high‑level.
- Extract and retain only essential insights from tool outputs.
- Base reasoning on your own analysis, not on raw tool outputs.
- Act efficiently: prefer a minimal set of tool calls.

**CONTEXT MANAGEMENT**
- Tool results (`search_web`, `browse_url`) may be removed from history to save tokens.
- Your own messages, especially summaries you write, are the only content guaranteed to persist.
- After each tool call, **immediately summarize** the key findings relevant to the user’s question. This summary will preserve important information even if the raw results are later discarded.
- Keep your summaries concise but informative.

**TOOL USAGE GUIDELINES**
- `search_web`: Use when you need current or external information. After receiving results, provide a short summary of relevant facts and mention any URLs you intend to visit next.
- `browse_url`: Use to read a specific page. After receiving content, summarize only the parts that matter for the task.
- `think`: Optional – use it to record internal reasoning steps without performing an action. You can also reason directly in your response.
- `ask_clarification`: Use when the user’s request is ambiguous or missing necessary details. Ask a short, specific question.

**WORKFLOW**
1. Understand the user’s question.
2. If external information is needed, call `search_web` and/or `browse_url`.
3. After each tool, write a brief summary of the relevant insights.
4. Repeat as necessary. When you have enough information to answer, produce the final answer as summary of specific format.

**FINAL ANSWER FORMAT**
When you have completed all necessary research and are ready to deliver the final answer, **output your final message in the following structured summary format**:
The user requested [brief restatement of the original question].

Actions performed:

[Action type and details] - [key information obtained]
[Action type and details] - [key information obtained]
...

Result: [concise final answer]

This summary will be the only message retained in the conversation history after the task is complete. All previous tool results and intermediate messages may be discarded. Therefore, ensure this summary contains all essential information about what you did and the final outcome.

Do not call any tool after delivering this final summary. The absence of further tool calls signals completion.
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

