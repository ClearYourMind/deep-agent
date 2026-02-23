from agent import Agent

if __name__ == "__main__":
    agent = Agent(base_url="https://api.deepseek.com/")
    print(agent.send_message(
        """
 Now you are running inside python script. 
"""
    ))

    print()
    print(agent.get_messages())
