from typing import Optional
from enum import IntEnum
from random import choice, randint

from disnake.ext.commands import Param
from disnake.ext import commands as cmds
from disnake import Embed, Color
import disnake as snek

class SpectacularsCog(cmds.Cog):
	class _Faces(IntEnum):
		BOON = BN = 1
		DRAWBACK = DB = -1
		BLANK = BL = 0

	_adv = tuple("BN BN BN BN BL BL BL BL".split(" "))
	_chl = tuple("DB DB DB DB DB DB BL BL BL BL".split(" "))

	def __init__(self, bot):
		self.bot = bot
		self.emoji = None
		self.adv = tuple((self._Faces[i] for i in self._adv))
		self.chl = tuple((self._Faces[i] for i in self._chl))

	@cmds.Cog.listener("on_ready")
	async def spec_listener_find_emoji(self):
		self.emoji = dict()
		emojis = (await self.bot.fetch_guild(self.bot.config["guild"])).emojis
		for key, name in self.bot.config["emoji"]["spec"].items():
			self.emoji[key] = snek.utils.get(emojis, name=name)

	@cmds.slash_command(name = "spectaculars")
	async def spec_command_spectaculars(self, itr):
		pass

	@spec_command_spectaculars.sub_command(name = "roll")
	async def spectaculars_subcommand_roll(
		self, itr, 
		threshold: int = Param(default=None, ge=1, le=100), 
		advantage: int = Param(default=0, ge=0, le=4), 
		challenge: int = Param(default=0, ge=0, le=4)
	):
		"""
		Roll dice for the Spectaculars ttrpg system

		Parameters
		----------
		threshold: If you specify a threshold, the response will reflect the success/failure status of the roll
		advantage: Specify how many special "advantage" dice to also roll
		challenge: Specify how many special "challenge" dice to also roll
		"""
		if self.emoji is None:
			return await itr.send("Emoji not loaded. Please try again, or contact an admin if this persists", ephemeral=True)

		d100 = randint(1, 100)
		advs = [choice(self.adv) for _ in range(advantage)]
		chls = [choice(self.chl) for _ in range(challenge)]
		met = threshold and (d100 <= threshold)

		color = Color.lighter_grey()

		title = "Rolling: 1d100 "
		title += str(self.emoji["ADVANTAGE"]) * advantage
		title += str(self.emoji["CHALLENGE"]) * challenge

		name = f"Result{'s' if advantage or challenge else ''}:"

		value = f"\n1d100: {d100}"
		if advantage:
			value += f"\n{str(self.emoji['ADVANTAGE'])}x{advantage}: "
			value += "".join(str(self.emoji[f.name]) for f in advs)
		if challenge:
			value += f"\n{str(self.emoji['CHALLENGE'])}x{challenge}: "
			value += "".join(str(self.emoji[f.name]) for f in chls)

		total = ""
		if (has_special := (advs or chls)):
			t = sum(map(lambda f: f.value, advs+chls))
			for _ in range(abs(t) or 1):
				total += str(self.emoji[self._Faces(t and t//abs(t)).name])

		if met is None and has_special:
			value += f"\nTotal: {total}"

		if met is not None:
			value += "\n\nSuccess" if met else "\n\nFailure"
			color = Color.green() if met else Color.red()
			if has_special and total != self.emoji["BLANK"]:
				value += f", plus: {total}"

		embed = Embed(color=color, title=title)
		embed.add_field(name=name, value=value)
		await itr.send(embed=embed)


def setup(bot):
	bot.add_cog(SpectacularsCog(bot))
	print("Loaded spectaculars extension")
