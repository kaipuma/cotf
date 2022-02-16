import re

from disnake.ext.commands import Param
from disnake.ext import commands as cmds
from disnake import Embed, Color
import disnake as snek

class UtilitiesCog(cmds.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.atcon = bot.config["autothread"]

	@cmds.Cog.listener("on_message")
	async def auto_thread_announcements(self, msg):
		"""Automatically creat a thread when one of the designated "Leader" roles sends a message in one of the designated channels"""
		if  msg.channel.id in self.atcon["channel_ids"] \
		and msg.author.top_role.id in self.atcon["leader_ids"] \
		and msg.role_mentions:
			name = "Discussion"
			if match := re.search(r"\[([^\]]*)\]", msg.content):
				name = match.groups()[0].capitalize()
			await msg.channel.create_thread(name=name, message=msg)

def setup(bot):
	bot.add_cog(UtilitiesCog(bot))
	print("Loaded utilities extension")
