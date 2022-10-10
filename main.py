import discord
from discord.ext import commands
from config import token, test_guild, tropa_guild, research_guild, repl
from live import keepAlive
from db.manage import scheduler
from os import system


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
            
        if not repl:
            await bot.tree.sync(guild=discord.Object(id=test_guild))
            await bot.tree.sync(guild=discord.Object(id=tropa_guild))
            await bot.tree.sync(guild=discord.Object(id=research_guild))
    
    async def on_ready(self):
        scheduler.start()
        print(f"Bot logged in as {self.user}")

        if not repl:
            system('echo "discord bot has been initialized" | festival --tts')

if repl:
    keepAlive()

bot = MyBot()    

async def remind_me(msg: str, channel_id: int = None, user_id: int = None):
    # get channel if reminder in server or user if privater reminder
    medium = await bot.fetch_channel(channel_id) if user_id is None else await bot.fetch_user(user_id)
    await medium.send(msg)

def run_bot():
    try:
        bot.run(token)
    except discord.errors.HTTPException:
        if repl:
            print("\n\n\nBLOCKED BY RATE LIMIT\nRESTARTING NOW\n\n\n")
            system("python restarter.py")
            system("kill 1")

if __name__ == '__main__':
    run_bot()