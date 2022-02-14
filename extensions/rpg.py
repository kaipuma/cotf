from disnake.ext import commands as cmds
import disnake as snek

class RPGCog(cmds.Cog):
	def __init__(self, bot):
		self.bot = bot

def setup(bot):
	bot.add_cog(RPGCog(bot))
	print("Loaded rpg extention")
