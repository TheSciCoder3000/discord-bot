import discord
from discord.ext import commands
from config import token, test_guild, tropa_guild, research_guild

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default(), command_prefix="$")
    
        self.initial_extensions = [
            "cogs.assessment.assessment",
            "cogs.subject.subject",
            "cogs.schedule.schedule",
            "cogs.classes.classes"
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        
        await bot.tree.sync(guild=discord.Object(id=test_guild))
        await bot.tree.sync(guild=discord.Object(id=tropa_guild))
        await bot.tree.sync(guild=discord.Object(id=research_guild))
    
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")


bot = MyBot()
bot.run(token)