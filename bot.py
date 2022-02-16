import json
import sys

import disnake as snek
from disnake.ext import commands as cmds

extensions = ["rpg", "utilities"]

try:
	with open("config/bot.json") as file:
		data = json.load(file)
	token = data["token"]
	guilds = data["guilds"]
	autothread = data["autothread"]
except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
	print("Please create the \"config/bot.json\" file based on the template")
	sys.exit()

bot = cmds.InteractionBot(test_guilds=guilds)
bot.config = {"autothread":autothread}
for name in extensions:
	bot.load_extension(f"extensions.{name}")

bot.run(token)
