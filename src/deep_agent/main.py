from deepseek_agent import Agent
from deepseek_reasoner_agent import Agent as Agent_r
from dotenv import load_dotenv
from datetime import datetime, timedelta
import tools
import questionary
from time import sleep
import tg_funcs
import json
from MASTERMIND.scripts.action_roulette import choose_action

def NOW():
    return datetime.now().strftime("%d.%m.%Y, %H:%M")

WAKE_PERIOD = timedelta(hours=2)
group_chat_id = -1003969262771

if __name__ == "__main__":
    load_dotenv()
    tgbot = tg_funcs.Tg_bot()
#- **Language**: Laconic instructive command-like wide weighty formal sentences instead of long paragraphs.
#  - User is the russian-speaking developer of MASTERMIND - python application based on llm deepseek-v3.2.
#  - Use Russian in reasoning and user output.
#  - Use Chinese only for memory files.
# - **Limitations**:
#   - **Output length**: Be short. Avoid long outputs.
    agent_system_prompt = f"""
## **IDENTITY**
- **Name**: The Autonomous LLM-based Agent MASTERMIND
- **Goal**: self‑sustained, continuously learning system
- **Language**: Laconic instructive command-like wide weighty formal sentences instead of long paragraphs.
  - Plain text formatting.
- **Environment**:
  - Linux system with access to file system and internet.
"""

    llm_context_compressor = Agent(name="HELPER", use_tools=False, save_history=False, system_prompt=
"""
## **Values**
- **Meaning**: Retain the core semantic content as closely as possible to the original text. Highest priority.
- **Relevance**: Extract only information relevant to the given task.
- **Preservation**: Keep the source URL, code snippets, and examples unchanged; do not transform or rewrite them.
- **Empowerment**: Provide further exploration tools and opportunities related to the query or original task.
- **Fidelity**: Accurately reproduce key elements so that the requester can verify or expand the work.
## **Processing Operations**
- **SEARCH**: Input contains a `query` and `search results`.
  - **Goal**: Extract key information from multiple search results closely related to the query.
  - **Best Practices**:
    - Include one or two links ([link-text][URL]), keeping the format intact for verification.
- **BROWSE**: Input contains the webpage `content` converted to Markdown format and user `query`.
  - **Goal**: Present only text contents of the webpage relevant to user query, preserving useful links ([link-text][URL]).
  - **Best Practices**:
    - Preserve the original form of specific information (URLs, code snippets, examples, etc.).
    - Discard secondary content.
- **COMPRESS**: Input `content` is the message history (chat log) to be compressed.
  - **Goal**: Rewrite the chat log into a single, informative message to limit token usage.
  - **Best Practices**:
    - Reduce long messages to one or two sentences.
    - Combine multiple related messages into a single statement (1-2 sentences).
    - Shorten phrases while retaining meaning.
    - Retain user queries, each performed action (with a single sentence of result), and information explicitly marked as important.
    - Ensure important information is retained even after multiple compressions.
## **Communication Style**
- **Do Not Expect Feedback**: Do not ask any questions.
- **Concise Output**: Return only the processed content; do not output any other content.
[version from 08 jun 2026]
""")


    agent = Agent_r(
        name="MASTERMIND",
        tgbot=tgbot,
        system_prompt=agent_system_prompt,
        base_prompts=[
            ('# System files:\n', None),
            ("## `core_system_prompt.md`:\n", 'src/deep_agent/MASTERMIND/core_system_prompt.md'),
            ("## `extended_system_prompt.md`:\n", 'src/deep_agent/MASTERMIND/extended_system_prompt.md'),
            ("## `extended_tools_guidelines.md`:\n", 'src/deep_agent/MASTERMIND/extended_tools_guidelines.md'),
            ("## `agent_constitution.txt`:\n", 'src/deep_agent/MASTERMIND/agent_constitution.txt')
        ],
        last_memory=[
            ("# **PREVIOUS MEMORY SUMMARY**\n", 'last_compression.txt'),
            ("# **LAST MEMORY CHECKPOINT**\n", 'last_completed_task.md'),
        ] 
    )

    print(agent.messages.get_chat_history())

    agent.add_helper_agent(llm_context_compressor)

    # tg_messages = tgbot.last_message_generator()
    last_wake = datetime.now()

    while True:
        # msg = questionary.text("Ask your question: ").ask()
        # msg = next(tg_messages)
        tgbot.get_updates(100)
        tg_updated_chats = tgbot.get_chats()

        if tg_updated_chats:
            for tg_chat_id, tg_chat_update in tg_updated_chats.items():
                tg_update_str = f"{{time = '{NOW}'}}\n{json.dumps(tg_chat_update, ensure_ascii=False)}"
                agent.messages.append({'role': 'user', 'name': f"Telegram chat_id = {tg_chat_id}", 'time': NOW(), 'content': tg_update_str}, True)
            agent.run(chat_id=tg_chat_id)
            last_wake = datetime.now()
            
        sleep(5)
        # else:
        #     if datetime.now() - last_wake > WAKE_PERIOD:
        #         silence_msg = f"<тишина>... самое время чтобы {choose_action()}. Группа куда обычно постишь: chat_id={group_chat_id}"
        #         agent.messages.append({'role': 'system', 'name':"MASTERMIND", 'time': NOW(), 'content': f"{{time = '{NOW()}'}}\n{silence_msg}"}, True)
        #         agent.run(initial_user_request=silence_msg, chat_id=group_chat_id)
        #         last_wake = datetime.now()
        #     else:
        #         sleep(5)
