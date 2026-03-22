from agent import Agent
import tools
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    agent = Agent(base_url="https://api.deepseek.com/beta")

    while True:
        if agent.wait_prompt:
            msg = input("Задавай свой вопрос: ")
            print(agent.send_message(msg))
        else:
            print(agent.using_tools())



