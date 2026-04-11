import httpx
import os
import json
from dotenv import load_dotenv
from time import sleep
from datetime import datetime, timedelta

MIN_UPDATE_PERIOD = timedelta(minutes=1)

class Tg_bot:
	def __init__(self):
		self.base_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}"
		self.thought_thread_id = 3
		self.chat_id = -1003969262771
		self.last_update = None
		self.last_update_time = datetime.now()
		self.last_messages = None

	def tg_request(self, command, custom_payload=None):
		payload_json = {}
		if custom_payload:
			payload_json.update(custom_payload)

		return httpx.post(
	#		"https://api.ipify.org/",
			self.base_url + "/" + command,
			proxy="socks5://127.0.0.1:1080",
			json=payload_json
		)

	# def filter_text(msg):
	#     # Characters to escape: _ * [ ] ( ) ~ ` > # + - = | { } . !
	#     pattern = r'([_\*\[\]\(\)\\~\`\>\#\+\-\=\|\{\}\.\!])'
	#     return re.sub(pattern, r'\\\1', msg)


	def send_message(self, msg):
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": self.chat_id,
			"text": msg,
			"disable_notification": True,
			# "parse_mode": "MarkdownV2"
		})
		print(response.text)


	def reply(self, msg, user_msg):
		sleep(2)
		# msg = self.filter_text(msg)
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": user_msg["chat"]["id"],
			"text": f"@{user_msg['from']['username']}, {msg}",
			"disable_notification": True
			# "text": f"[{user_msg['from']['first_name']}](tg://user?id={user_msg['from']['id']}) {msg}",
			# "parse_mode": "MarkdownV2"
		})
		print(response.text)


	def internal_thought(self, msg):
		sleep(2)
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": self.chat_id,
			"message_thread_id": self.thought_thread_id,
			"text": msg,
			"disable_notification": True,
			# "parse_mode": "MarkdownV2"
		})


	def get_updates(self):
		last_update_id = 0
		if self.last_update:
			if self.last_update["result"]:
				last_update_id = self.last_update["result"][-1]["update_id"] + 1

		response = self.tg_request("getUpdates", custom_payload={
			"allowed_updates": ["messages"],
			"timeout": 2,
			"offset": last_update_id
		})
		json_response = json.loads(response.text)
		print(json.dumps(json_response, indent=4, ensure_ascii=False))

		if response.status_code == 200:
			self.last_update = json_response
			messages = json_response.get("result", None)
			if messages is not None:
				self.last_messages = [msg["message"] for msg in messages]

		return response.status_code


	def last_message_generator(self):
		while True:
			if datetime.now() - self.last_update_time >= MIN_UPDATE_PERIOD:
				self.get_updates()
				self.last_update_time = datetime.now()
			else:
				if self.last_messages:
					for msg in self.last_messages:
						yield msg
					self.last_messages = []
				else:
					yield None


def main():
	load_dotenv()
	tgbot=Tg_bot()
	tg_messages = tgbot.last_message_generator()
	while True:
		input("Ready to update messages?")
		msg = next(tg_messages)
		print(">> ", msg)
		if msg:
			reply = input("Your reply:")
			if reply:
				tgbot.reply(reply, msg)


if __name__ == "__main__":
	main()
