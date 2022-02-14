import json
import sys

import disnake as snek
from disnake.ext import commands as cmds

extensions = ["rpg"]

try:
	with open("config/bot.json") as file:
		data = json.load(file)
	token = data["token"]
	guilds = data["guilds"]
except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
	print("Please create the \"config/bot.json\" file based on the template")
	sys.exit()

bot = cmds.InteractionBot(test_guilds=guilds)

for name in extensions:
	bot.load_extension(f"extensions.{name}")

bot.run(token)
