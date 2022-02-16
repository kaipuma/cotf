from datetime import datetime as dt
from enum import Enum
import re
from typing import Optional

from disnake.ext.commands import Param
from disnake.ext import commands as cmds
from disnake import Embed, Color
import disnake as snek

class UtilitiesCog(cmds.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.atcon = bot.config["autothread"]
		self.fbchan = None

	@cmds.Cog.listener("on_message")
	async def utilities_listener_auto_thread_announcements(self, msg):
		"""Automatically create a thread when one of the designated "Leader" roles sends a message in one of the designated channels"""
		if  msg.channel.id in self.atcon["channel_ids"] \
		and msg.author.top_role.id in self.atcon["leader_ids"] \
		and msg.role_mentions:
			name = "Discussion"
			if match := re.search(r"\[([^\]]*)\]", msg.content):
				name = match.groups()[0].capitalize()
			await msg.channel.create_thread(name=name, message=msg)

	@cmds.Cog.listener("on_ready")
	async def utilities_listener_load_feedback_channel(self):
		self.fbchan = await self.bot.fetch_channel(self.bot.config["feedback_channel_id"])

	class _FeedbackType(Color, Enum):
		Suggestion = Color.blurple().value
		Commands = Color.yellow().value
		Bug = Color.magenta().value
		Compliment = Color.green().value
		Issue = Color.red().value
		Other = Color.blurple().value

	@cmds.slash_command(name="feedback")
	async def utilities_command_feedback(
		self, itr, feedback: str, 
		kind: _FeedbackType = Param(
			default = _FeedbackType.Other, 
			name = "type",
			description = "Optionally specify the type of feedback being given"
		)
	):
		"""
		Submit feedback/suggestions about this bot or the server

		Parameters
		----------
		feedback: The text that will be sent to the admin team
		"""
		if self.fbchan is None:
			return await itr.send("Sorry, there was an error. Please contact an admin directly")

		kind = self.__class__._FeedbackType(kind)

		embed = Embed(
			color = kind.value,
			title = f"{kind.name} submitted by {itr.author.display_name}:",
			description = feedback
		).set_footer(
			text = f"{itr.author.display_name}'s id: {itr.author.id}",
			icon_url = itr.author.display_avatar
		)

		await self.fbchan.send(embed=embed)
		await itr.send("I've submitted that feedback for you", ephemeral=True)

def setup(bot):
	bot.add_cog(UtilitiesCog(bot))
	print("Loaded utilities extension")
