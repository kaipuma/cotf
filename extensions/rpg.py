from typing import Optional, Union
from inspect import cleandoc as dedent

from disnake.ext.commands import Param
from disnake.ext import commands as cmds
from disnake import Embed, Color
import disnake as snek
from d20 import roll, RollError

class RPGCog(cmds.Cog):
	def __init__(self, bot):
		self.bot = bot

	@cmds.slash_command(
		name="roll",
		description="Roll some dice"
	)
	async def rpg_command_roll(self, itr, dice: str):
		"""
		Roll some amount of dice

		Parameters
		----------
		dice: Specify what to roll. See the /dice command for help.
		"""
		try:
			await itr.send(f"Your result is: {roll(dice)}")
		except RollError:
			await itr.send((
				f"Something went wrong trying to process \"{dice}\". "
				"Please check that you typed it right and try again.\n"
				"(hint: use /dice for a full explanation of the /roll command syntax)"
			), ephemeral=True)

	@cmds.slash_command(
		name="dice",
		description="How to use the /roll command"
	)
	async def rpg_command_dice(self, itr):
		"""
		Show the user all the options available in the /roll command
		"""
		await itr.send(
			dedent("""
			When using the /roll command, enter all the dice you wish, then press tab to confirm, then press enter to submit.
			Specify dice in the form "XdY", where X and Y are numbers, and X is optional and defaults to 1.
			You may specify any number of types of dice, adding them together with a plus sign (+). All individual rolls will be shown, as well as the total.
			Additionally, you may add any number of operators to change the results. Each operator is followed by a selector.
			The operators and selectors are as follows ("X" in selectors represents a number):
			```
			operator | use | description
			-------------------------------
			keep     | k   | keep all matched values
			drop     | p   | drop all matched values
			reroll   | rr  | rerolls all matched values until none match
			rr once  | ro  | rerolls all matched values once
			rr & add | ra  | rerolls up to one matched value once, keeping the original roll also
			explode  | e   | rolls another die for each matched value
			minimum  | mi  | sets the minimum value of each die
			maximum  | ma  | sets the maximum value of each die

			selector | use | description
			-------------------------------
			literal  | X   | all values that are exactly this value
			highest  | hX  | the X number of highest values
			lowest   | lX  | the X number of lowest values
			greater  | >X  | all values greater than X
			less     | <X  | all values less than X
			```
			In addition to dice and their modifiers/selectors, basic mathematical and comparison operators can be used.
			Also sets can be formed by enclosing a list of values in parens. Only the keep and drop operators are usable on non-dice sets.
			Lastly, you can annotate the roll with comments in [square brackets]. These have no function, but can be used, for example, to specify damage type
			Here are a selection of valid /roll commands:
			4d6 + d8 + 2
			1d8 [slashing] + 3d6 [fire]
			20d6e6
			2d20kh1 [advantage]
			(2, 2, d6, d6)kl2

			If you wish to see the full details of the dice parser, see https://d20.readthedocs.io/en/latest/start.html#dice-syntax
			"""),
			ephemeral=True
		)

	@cmds.slash_command(
		name="xcard",
		description="Invoke the x-card (anonymously)"
	)
	async def rpg_command_xcard(self, itr, details: Optional[str] = None, role: Optional[snek.Role] = None):
		"""
		Evoke the rpg safety tool called the "x-card" in the current channel

		Parameters
		----------
		details: Optionally you may provide more detail as to why you invoked the x-card
		role: Optionally you may specify a role to ping. @here is used by default
		"""
		ping = role.mention if role is not None else "@here"

		embed = Embed(color=Color.red(), title="X-Card Invoked!")
		if details is not None:
			embed.add_field("They added the following details:", details)

		channel = await self.bot.fetch_channel(itr.channel_id)
		await itr.send("I'll let everyone else know.", ephemeral=True)
		await channel.send(ping, embed=embed)

	@cmds.slash_command(
		name="ocard",
		description="Invoke the o-card (optionally anonymously)"
	)
	async def rpg_command_xcard(
		self, 
		itr, 
		details: Optional[str] = None, 
		mention: Optional[Union[snek.Role, snek.Member]] = None, 
		anonymous: bool = True
	):
		"""
		Evoke the "o-card" in the current channel
		This is the inverse of the "x-card", and signals that you're having a good time

		Parameters
		----------
		details: Optionally you may provide more detail as to why you invoked the o-card
		mention: Optionally you may specify a role or user to ping. @here is used by default
		anonymous: You may elect to reveal that it was you who invoked this
		"""
		ping = mention.mention if mention is not None else "@here"

		embed = Embed(color=Color.green(), title=f"O-Card Invoked!")
		if details is not None:
			embed.add_field("They added the following details:", details)
		if not anonymous:
			avatar = itr.author.guild_avatar or itr.author.avatar
			name = itr.author.nick or itr.author.name
			embed.set_footer(text=f"Sent by {name}", icon_url=avatar.url)

		channel = await self.bot.fetch_channel(itr.channel_id)
		await itr.send("I'll let everyone else know.", ephemeral=True)
		await channel.send(ping, embed=embed)

def setup(bot):
	bot.add_cog(RPGCog(bot))
	print("Loaded rpg extension")
