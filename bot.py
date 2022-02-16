import json
import sys

import disnake as snek
from disnake.ext import commands as cmds

try:
	with open("config/bot.json") as file:
		data = json.load(file)
	with open("config/template.bot.json") as file:
		template = json.load(file)
	if not set(data.keys()) == set(template.keys()) \
	or any(value in data.values() for value in template.values()):
		raise KeyError
except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
	print("Please create the \"config/bot.json\" file based on the template in \"config/template.bot.json\"")
	sys.exit()

bot = cmds.InteractionBot(test_guilds=data["guilds"])
bot.config = data
for name in data["extensions"]:
	bot.load_extension(f"extensions.{name}")

bot.run(data["token"])
