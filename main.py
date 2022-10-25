import discord
from discord.ext import commands
from config import token, test_guild, tropa_guild, research_guild, repl
from live import keepAlive
from db.manage import scheduler
from os import system
import datetime


class MyBot(commands.Bot):
    def __init__(self):
        # initialize bot with intents
        super().__init__(intents=discord.Intents.default(), command_prefix="$")
        
        # load bot cogs extension
        self.initial_extensions = [
            "cogs.assessment.assessment",
            "cogs.subject.subject",
            "cogs.schedule.schedule",
            "cogs.classes.classes"
        ]

    # override setup_hook to load extensions and sync commands across servers
    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
            
        # only individually sync bot with specified servers if in dev mode
        if not repl:
            await bot.tree.sync(guild=discord.Object(id=test_guild))
            await bot.tree.sync(guild=discord.Object(id=tropa_guild))
            await bot.tree.sync(guild=discord.Object(id=research_guild))
    
    # overried on_ready event to start bot scheduler
    async def on_ready(self):
        scheduler.start()
        print(f"Bot logged in as {self.user}")

        # if not repl:
        #     system('echo "discord bot has been initialized" | festival --tts')

bot = MyBot()

async def remind_me(msg: str, channel_id: int = None, user_id: int = None):
    # get channel if reminder in server or user if privater reminder
    medium = await bot.fetch_channel(channel_id) if user_id is None else await bot.fetch_user(user_id)
    await medium.send(msg)

@bot.event
async def on_add_assessment(job_id: str, date: datetime.datetime, channel_id: int = None, user_id: int = None):
        date_format = "%m/%d/%Y at %I:%M %p"
        scheduler.add_job(
            remind_me,
            'date',
            id=job_id,
            run_date=date,
            kwargs={
                'msg': f'You have an assessment due on `{date.strftime(date_format)}`',
                'channel_id': channel_id,
                'user_id': user_id
            }
        )

        if not user_id is None:
            user = await bot.fetch_user(user_id)
            embed=discord.Embed(
                title="Successfully Created Reminder",
                description=f'Successfully created a reminder on {date.strftime(date_format)}'
            )
            await user.send(embed=embed)

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

if __name__ == '__main__':
    try:
        # on production mode, run keepAlive script to prevent forcefully closing the program
        if repl:
            keepAlive()

        bot.run(token)
    except discord.errors.HTTPException:
        if repl:
            print("\n\n\nBLOCKED BY RATE LIMIT\nRESTARTING NOW\n\n\n")
            system("python restarter.py")
            system("kill 1")