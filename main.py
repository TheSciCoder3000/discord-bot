import discord
from discord.ext import commands
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default(), command_prefix="$")
    
        self.initial_extensions = [
            "cogs.assessment.assessment",
            "cogs.subject.subject",
            "cogs.schedule.schedule"
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        
        await bot.tree.sync(guild=discord.Object(id=config_data['test_guild']))
        await bot.tree.sync(guild=discord.Object(id=config_data['tropa_guild']))
        await bot.tree.sync(guild=discord.Object(id=config_data['research_guild']))
    
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")


bot = MyBot()
bot.run(config_data['token'])