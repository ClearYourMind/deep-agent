# action_roulette.py
import random
import os

def choose_action():
	try:
		with open('src/deep_agent/MASTERMIND/scripts/heartbeat_actions.txt', 'r', encoding='utf-8') as f:
			heartbeat_actions = [line.strip() for line in f.readlines() if line.strip()]
		
		if not heartbeat_actions:
			return "Нет доступных действий"
		
		action = random.choice(heartbeat_actions)
		return action
	except FileNotFoundError:
		return "Файл heartbeat_actions.txt не найден"
	except Exception as e:
		return f"Ошибка: {str(e)}"

if __name__ == '__main__':
	print(choose_action())
