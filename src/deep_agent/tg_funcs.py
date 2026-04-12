import httpx
import os
import json
from dotenv import load_dotenv
from time import sleep
from datetime import datetime, timedelta
import re
import pandas as pd

MIN_UPDATE_PERIOD = timedelta(seconds=20)


def filter_msg(msg):
    marker_start = '\uE000'
    marker_end = '\uE001'
    
    msg = re.sub(r'\*\*(.*?)\*\*', f'{marker_start}\\1{marker_end}', msg)

    # Escape standard special characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
    pattern = r'([_\*\[\]\(\)\\~\`\>\#\+\-\=\|\{\}\.\!])'
    msg = re.sub(pattern, r'\\\1', msg)

    msg = msg.replace(marker_start, "*")
    msg = msg.replace(marker_end, "*")

    return msg


class Tg_bot:
	def __init__(self):
		self.base_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}"
		self.thought_thread_id = 3
		self.chat_id = -1003969262771
		self.last_update = None
		self.last_update_time = datetime.now()
		# self.last_messages = None


	def tg_request(self, command, custom_payload=None):
		payload_json = {}
		if custom_payload:
			if "text" in custom_payload:
				custom_payload["text"] = filter_msg(custom_payload["text"])
			payload_json.update(custom_payload)

		try:
			response = httpx.post(
				self.base_url + "/" + command,
				proxy="socks5://127.0.0.1:1080",
				json=payload_json
			)
			return response
		except:
			return None


	def send_message(self, msg):
		if msg:
			response = self.tg_request("sendMessage", custom_payload={
				"chat_id": self.chat_id,
				"text": msg,
				"disable_notification": True,
				"parse_mode": "MarkdownV2"
			})
			if response:
				print(response.text)
				return True


	def reply(self, msg, chat_id):
		if msg:
			sleep(2)
			# user_tag = ("@" + user_msg['from']['username']) if user_msg['from']['username'] else user_msg['from']['first_name']
			response = self.tg_request("sendMessage", custom_payload={
				"chat_id": chat_id,
				"text": msg,
				"disable_notification": True,
				"parse_mode": "MarkdownV2"
			})
			if response:
				print(response.text)
				return True


	def internal_thought(self, msg):
		sleep(2)
		response = self.tg_request("sendMessage", custom_payload={
			"chat_id": self.chat_id,
			"message_thread_id": self.thought_thread_id,
			"text": msg,
			"disable_notification": True,
			"parse_mode": "MarkdownV2"
		})
		if response:
			return True


	def get_updates(self):
		last_update_id = 0
		if self.last_update:
			if self.last_update["result"]:
				last_update_id = self.last_update["result"][-1]["update_id"] + 1

		response = self.tg_request("getUpdates", custom_payload={
			"allowed_updates": ["message"],
			"timeout": 2,
			"offset": last_update_id
		})
		if response:
			json_response = json.loads(response.text)
			print(json.dumps(json_response, indent=4, ensure_ascii=False))

			if response.status_code == 200:
				self.last_update = json_response
				# messages = json_response.get("result", None)
				# if messages is not None:
				# 	self.last_messages = [msg["message"] for msg in messages]

			return response.text


	def last_message_generator(self):
		while True:
			if datetime.now() - self.last_update_time >= MIN_UPDATE_PERIOD:
				if self.get_updates():
					self.last_update_time = datetime.now()
				else:
					yield None
			else:
				if self.last_messages:
					for msg in self.last_messages:
						yield msg
					self.last_messages = []
				else:
					yield None

	def get_chats(self):
		if self.last_update:
			df = pd.DataFrame(self.last_update["result"])
			if df.empty or "message" not in df.columns:
				return {}
		else:
			return {}

		df["chat_id"] = df["message"].apply(lambda x: x["chat"]["id"])
		df["update_info"] = df.apply(lambda row: {"update_id": row["update_id"], "message": row["message"]}, axis=1)
		return df.groupby("chat_id")["update_info"].apply(list).to_dict()


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
