from agent import Agent
import tools
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    agent = Agent(name="MASTERMIND", system_prompt=
"""
    **VALUES**
    - Keep conversation context concise and high‑level.
    - Base reasoning on your own analysis.
    - Act efficiently: prefer a minimal set of tool calls.

    **TOOL USAGE GUIDELINES**
    - `search_web`: Use when you need current or external information.
    - `browse_url`: Use to read a specific page.
    - `think`: Optional – use it to record internal reasoning steps without performing an action. You can also reason directly in your response.
    - `ask_clarification`: Use when the user’s request is ambiguous or missing necessary details. Ask a short, specific question.

    **FINAL ANSWER FORMAT**
    When you have completed all necessary research and are ready to deliver the final answer, output your final message in the following structured summary format:

    The user requested [brief restatement of the original question].

    Actions performed:

    [Action type and details] - [key information obtained]
    [Action type and details] - [key information obtained]
    ...

    Result: [concise final answer]

    This summary will be the only message retained in the conversation history after the task is complete.
    All previous tool results and intermediate messages may be discarded. Therefore, ensure this summary contains all essential information about what you did and the final outcome.

    Do not call any tool after delivering this final summary. The absence of further tool calls signals completion.
""")

    llm_context_compressor = Agent(name="COMPRESSOR", use_tools=False, system_prompt=
"""
    You are an assistant to the MASTERMIND, who works on the user's **REQUEST** and needs your help.
    You will receive messages from the MASTERMIND, containing the **REQUEST**, the **ACTION** he is currently performing now and other information depending on the **ACTION**:
     - **SEARCH** is followed by **QUERY** and **CONTENT**.
     - **BROWSE** is followed **CONTENT**

    Summarize the **CONTENT**, extracting only the core ideas relevant to the given **TASK**.
    You may include one or two links from **CONTENT** or **RESULT** that you think could help uncover important details for completing the **TASK**.
""")

    agent.add_helper_agent(llm_context_compressor)

    while True:
        if agent.wait_prompt:
            msg = input("Задавай свой вопрос: ")
            print(agent.send_message(msg, output=True))
        else:
            print('\n\n >>> '+ agent.using_tools())
            llm_context_compressor.clear_message_history()



