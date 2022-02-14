import json
import sys

import disnake as snek
from disnake.ext import commands as cmds

try:
	with open("config/bot.json") as file:
		data = json.load(file)
	token = data["token"]
	guilds = data["guilds"]
except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
	print("Please create the \"config/bot.json\" file based on the template")
	sys.exit()

bot.run(token)