from disnake.ext.commands import Param
from disnake.ext import commands as cmds
from disnake import Embed, Color
import disnake as snek

from .modules.sw import Roll, SWDice

def _gen_roll_option(name: str) -> Param:
	return Param(
		name = name,
		description = f"The numer of {SWDice[name.upper()].name.lower()} ({name}) dice to roll.",
		ge = 0,
		default = 0,
		convert_defaults = True
	)

@cmds.register_injection
def _roll_inj(
	itr,
	yellow: int = _gen_roll_option("yellow"),
	green: int = _gen_roll_option("green"),
	blue: int = _gen_roll_option("blue"),
	white: int = _gen_roll_option("white"),
	black: int = _gen_roll_option("black"),
	purple: int = _gen_roll_option("purple"),
	red: int = _gen_roll_option("red")
) -> Roll:
	return Roll(y=yellow, g=green, b=blue, w=white, k=black, p=purple, r=red)

class StarWarsCog(cmds.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.emoji = None

	@cmds.Cog.listener("on_ready")
	async def sw_listener_find_emoji(self):
		self.emoji = dict()
		emojis = (await self.bot.fetch_guild(self.bot.config["guild"])).emojis
		for key, name in self.bot.config["emoji"]["sw"].items():
			self.emoji[key] = snek.utils.get(emojis, name=name)

	@cmds.slash_command(name = "starwars")
	async def sw_command_starwars(self, itr):
		pass

	@sw_command_starwars.sub_command(name = "roll")
	async def starwars_subcommand_roll(self, itr, roll: Roll):
		"""
		Roll some dice for the FFG SW TTRPG
		"""
		title = "Rolling: "
		value = ""
		total = ""
		for die, faces in roll.results.items():
			if not roll[die]:
				continue
			title += str(roll[die]) + str(emoji := self.emoji[die.color])
			value += f"\n{roll[die]}{emoji}: "
			value += " + ".join("".join(str(self.emoji[s.name]) for s in f) for f in faces)

		value += "\n\nTotal: "
		for sym, num in roll.total.items():
			value += str(self.emoji[sym.name]) * num

		embed = Embed(
			color = Color.lighter_grey(),
			title = title
		).add_field(
			name = "Results:",
			value = value
		)

		await itr.send(embed=embed)

def setup(bot):
	bot.add_cog(StarWarsCog(bot))
	print("Loaded star wars extension")
