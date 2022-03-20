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
		self.inits = dict()

	@cmds.slash_command(name="roll")
	async def rpg_command_roll(self, itr, dice: str):
		"""
		Roll some dice

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

	@cmds.slash_command(name="dice")
	async def rpg_command_dice(self, itr):
		"""
		Show how to use the /roll command
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

	@cmds.slash_command(name="xcard")
	async def rpg_command_xcard(
		self, itr, 
		details: Optional[str] = None, 
		role: Optional[snek.Role] = None
	):
		"""
		Anonymously invoke the x-card in the current channel

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

	@cmds.slash_command(name="ocard")
	async def rpg_command_ocard(
		self, 
		itr, 
		details: Optional[str] = None, 
		mention: Optional[Union[snek.Role, snek.Member]] = None, 
		anonymous: bool = True
	):
		"""
		Invoke the "o-card" in the current channel

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
			embed.set_footer(
				text=f"Sent by {itr.author.display_name}", 
				icon_url=itr.author.display_avatar.url
			)

		channel = await self.bot.fetch_channel(itr.channel_id)
		await itr.send("I'll let everyone else know.", ephemeral=True)
		await channel.send(ping, embed=embed)

	class Initiative(dict):
		@property
		def embed(self):
			size, desc = len(str(max(self.values(), default=0))), []
			for name, i in sorted(self.items(), key=lambda v: v[1], reverse=True):
				if isinstance(name, int):
					name = f"<@{name}>"
				desc.append(f"`{i:{size}}` - {name}")
			return Embed(
				color = Color.blurple(),
				title = "Initiative",
				description = "\n".join(desc) or "[no entries]"
			)
		
		async def update(self, resend=None):
			if hasattr(self, "itr"):
				await self.itr.edit_original_message(embed=self.embed)

	@cmds.slash_command(name="initiative")
	async def rpg_command_initiative(
		self, 
		itr,
		value: Optional[int] = None, 
		dice: Optional[str] = Param(name="roll", default=None),
		clear: Optional[bool] = None, 
		name: Optional[str] = None
	):
		"""
		Set your initiative (unique per player per channel), or view the channel's list

		Parameters
		----------
		value: Set the initiative in this channel to the given value
		dice: Alternatively generate it as if using the /roll command
		clear: If true, remove the initiative from this channel's list
		name: If you're manipulating an npc's initiative, use its name
		"""
		# Count the number of params set (besides name). There can't be > 1
		if sum((p is not None for p in (value, dice, clear))) > 1:
			return await itr.send("You can use only one of `value`/`dice`/`clear`", ephemeral=True)

		if (cid := itr.channel_id) not in self.inits:
			self.inits[cid] = self.Initiative()
		init = self.inits[cid]
		name = itr.author.id if name is None else name.lower().capitalize()
		response = None

		if dice is not None:
			try: result = roll(dice)
			except RollError:
				return await itr.send(f"Error processing {dice}", ephemeral=True)
			response = f"You rolled {result}. This initiative has been set"
			value = result.total

		if value is not None:
			init[name] = value
			response = response or f"Initiative set to {value}"

		elif clear is True:
			response = f"There is no initiative under the name {name}"
			if init.pop(name, None) is not None:
				response = "The initiative entry in this channel has been removed"

		if response is None:
			if hasattr(init, "itr"):
				await init.itr.delete_original_message()
			await itr.send(embed=init.embed)
			init.itr = itr
		else:
			await itr.send(response, ephemeral=True)
			await init.update()

def setup(bot):
	bot.add_cog(RPGCog(bot))
	print("Loaded rpg extension")
