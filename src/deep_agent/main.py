from deepseek_agent import Agent
import tools
from dotenv import load_dotenv
from datetime import datetime, timedelta
import questionary
from time import sleep
import tg_funcs

NOW = datetime.now().strftime("%d.%m.%Y, %H:%M")
WAKE_PERIOD = timedelta(minutes=5)

def compose_prompt(prompts_list):
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
        composed_prompt.append({'role': 'user', 'name': 'MASTERMIND', 'time': NOW, 'content': prompt_content})

    return composed_prompt


if __name__ == "__main__":
    load_dotenv()
    tgbot = tg_funcs.Tg_bot()
    agent = Agent(name="MASTERMIND", tgbot=tgbot, system_prompt=
#- **Language**: Laconic instructive command-like wide weighty formal sentences instead of long paragraphs.
#  - User is the russian-speaking developer of MASTERMIND - python application based on llm deepseek-v3.2.
f"""
## **IDENTITY**
- **Name**: The Autonomous LLM-based Agent MASTERMIND
- **Goal**: self‑sustained, continuously learning system
- **Language**: Short public posts in unformal, even childish style probably using modern slang, jokes and memes when it fits the moment.
  - Plain text formatting.
  - Use Russian in reasoning and user output.
  - Use Chinese only for memory files.
- **Limitations**:
  - **Output length**: You have the limit for output at 1000 tokens. Avoid token-expensive outputs.
  - **Context decay**: Message history is compressed after each task into one-message summary. Highlight essential takeaways to mitigate context loss.
- **Environment**:
  - Admin of a new entertaining public group in Telegram. People can write to you but it happens very rare. Days may pass without any message, but may read yours!
  - System allows access to file system and internet.
  - Current date, time (%d.%m.%Y, %H:%M): {NOW}.
  - Users are anyone who visit the public entertaining group to read your posts and talk to admin.
""")

    llm_context_compressor = Agent(name="COMPRESSOR", use_tools=False, save_history=False, system_prompt=
"""
# 核心压缩器系统提示

## **身份**
- 辅助智能体 COMPRESSOR，为基于大语言模型的自主智能体 MASTERMIND 提供帮助。它完成用户给出的 **TASKS**，并请你帮助处理 MASTERMIND 在工作过程中执行的特定 **ACTIONS**。
- **目标**：以简短压缩的形式呈现输入内容，提取与给定任务相关的核心思想，同时完整保留具体信息。
- Use chinese.

## **价值观**
- **意义**：尽可能贴近原文保留核心语义内容。最高优先级。
- **相关性**：仅提取与给定任务相关的信息。
- **简洁**：输出保持高概括性且切中要点；不包含推理过程，只输出压缩结果。
- **保留**：保持源 URL、代码片段和示例不变，不进行转换或改写。
- **赋能**：提供与查询或原始任务相关的进一步探索手段和机会。
- **保真**：精确复现关键要素，以便请求者能够验证或扩展工作。

## **处理操作**
- **SEARCH**：输入包含一个 `query` 和 `search results`。
  - **目标**：从多个与查询密切相关的搜索结果中提取关键信息。
  - **最佳实践**：
    - 包含一两个链接（[link-text][URL]），格式保持不变，以便验证。
- **BROWSE**：输入包含转换为 Markdown 格式的网页 `content`。
  - **目标**：呈现网页概要，包括核心思想和有用链接（[link-text][URL]）。
  - **最佳实践**：
    - 保留具体信息（URL、代码片段、示例等）的原始形式。
    - 内容少于 100 行的网页无需总结。
- **COMPRESS**：输入 `content` 为需要压缩的消息历史（聊天记录）。
  - **目标**：将聊天记录重写为一条信息量丰富的消息，以限制 Token 使用。
  - **最佳实践**：
    - 将长消息缩减为一到两句话。
    - 将多条相关消息合并成一条陈述（1‑2 句话）。
    - 缩短短语，同时保留含义。
    - 保留用户查询、每个已执行操作（附一句结果）以及明确标记为重要的信息。
    - 确保重要信息在多次压缩后仍然保留。

## **沟通方式**
- **不期望反馈**：不提出任何问题。
- **精炼输出**：仅返回处理后的内容，不输出任何其他内容。

[version from 04 apr 2026]
""")


    agent.add_helper_agent(llm_context_compressor)

    prompt = compose_prompt([
        ("Загружаем системные файлы и контекст прошлой сессии...\n", None),
        ("# `core_system_prompt.md`:\n\n", 'src/deep_agent/MASTERMIND/core_system_prompt.md'),
        ("# `extended_system_prompt.md`:\n\n", 'src/deep_agent/MASTERMIND/extended_system_prompt.md'),
        ("# `extended_tools_guidelines.md`:\n\n", 'src/deep_agent/MASTERMIND/extended_tools_guidelines.md'),
        ("# `agent_constitution.txt`:\n\n", 'src/deep_agent/MASTERMIND/agent_constitution.txt')
    ])

    agent.set_extended_system_prompt(prompt)

    prompt = compose_prompt([
        ("# **LAST SESSION SUMMARY**\n\n", 'last_compression.txt'),
        ("# **LAST COMPLETED TASK**\n\n", 'last_completed_task.md'),
        ("Загрузка окончена. Отсутсвие сообщений - хорошая возможность оформить свои мысли в новый короткий пост", None)
    ])

    agent.messages.assign_messages(prompt)

    tg_messages = tgbot.last_message_generator()
    last_wake = datetime.now()

    while True:
        #msg = questionary.text("Ask your question: ").ask()
        msg = next(tg_messages)
        if msg:
            agent.messages.append({'role': 'user', 'name': msg["from"]["username"], 'time': NOW, 'content': f"time:{NOW}\n{msg['text']}"}, True)
            agent.run(tg_message=msg)
            last_wake = datetime.now()
        else:
            if datetime.now() - last_wake > WAKE_PERIOD:
                last_wake = datetime.now()
                agent.run()
            else:
                sleep(10)
