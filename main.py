import discord
from discord.ext import commands
from config import token, test_guild, tropa_guild, research_guild
from live import keepAlive
from db.manage import scheduler

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
        scheduler.start()
        print(f"Bot logged in as {self.user}")

# keepAlive()
bot = MyBot()

@bot.event
async def on_add_schedule(day: str, sched_id: str, subject_name: str, time_start, channel_id: int):
    time_str = time_start.strftime("%I:%M %p")
    scheduler.add_job(
        remind_me, 
        'cron',
        day_of_week=day,
        hour=time_start.hour,
        minute=time_start.minute,
        id=sched_id,
        kwargs={
            "msg": f"You have a schedule for {subject_name} at {time_str}",
            'channel_id': channel_id
        }
    )
    print('scheduler has been added')

async def remind_me(msg: str, channel_id: int):
    channel = bot.get_channel(channel_id)
    await channel.send(msg)

bot.run(token)