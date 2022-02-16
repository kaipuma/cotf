import json
import sys

import disnake as snek
from disnake.ext import commands as cmds

try:
	with open("config.json") as file:
		data = json.load(file)
	with open("template.config.json") as file:
		template = json.load(file)
	if not set(data.keys()) == set(template.keys()) \
	or any(value in data.values() for value in template.values()):
		raise KeyError
except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
	print("Please create the \"config.json\" file based on the template in \"template.config.json\"")
	sys.exit()

bot = cmds.InteractionBot(test_guilds=data["guilds"] or None)
bot.config = data
for name in data["extensions"]:
	bot.load_extension(f"extensions.{name}")

bot.run(data["token"])
