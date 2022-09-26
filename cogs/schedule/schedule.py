import discord
from typing import List
from configparser import ConfigParser
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from db.manage import Connection, Subject, Schedule, SubjectClass
from dateutil.parser import parse
from .schedMenu import ScheduleSaveMenu


config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']


class Schedules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dayList = [
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
        ]

    @app_commands.command(name='add-sched', description="add a new schedule to a class")
    @app_commands.describe(time_in="what time the class starts")
    @app_commands.describe(time_out="what time the class ends")
    @app_commands.describe(day="what day of the week this schedule is")
    @app_commands.choices(day = [
        Choice(name = 'Sunday', value = 0),
        Choice(name = 'Monday', value = 1),
        Choice(name = 'Tuesday', value = 2),
        Choice(name = 'Wednesday', value = 3),
        Choice(name = 'Thursday', value = 4),
        Choice(name = 'Friday', value = 5),
        Choice(name = 'Saturday', value = 6),
    ])
    async def add_sched(
        self,
        interaction: discord.Interaction,
        time_in: str,
        time_out: str,
        day: int,
        subject: int
    ):

        with Connection() as con:
            subject_data = con.query(Subject).filter_by(id=subject).first()
            class_data = subject_data.classes

            embed=discord.Embed(title="New Schedule", description="details of your newly created schedule", color=0xff7800)
            embed.set_author(name=f"@{interaction.user}")
            embed.add_field(name="Subject", value=subject_data.code, inline=False)
            embed.add_field(name="Day", value=self.dayList[day], inline=True)
            str_time_start = parse(time_in).strftime("%I:%M %p")
            str_time_end = parse(time_out).strftime("%I:%M %p")
            embed.add_field(name="Time", value=f"{str_time_start} - {str_time_end}", inline=True)

            if len(class_data) == 1:
                sched = Schedule(
                    weekdays=day, 
                    time_in=parse(time_in).time(), 
                    time_out=parse(time_out).time(), 
                    guild_id=interaction.guild.id,
                    sched_class=class_data[0]
                )

                view = ScheduleSaveMenu(sched, embed)

                await interaction.response.send_message(embed=embed, view=view)
    
    @add_sched.autocomplete('subject')
    async def add_sched_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        subjects = []
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
            ]

        return subjects


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Schedules(bot), guilds=[
        discord.Object(id=config_data['test_guild']),
        discord.Object(id=config_data['tropa_guild']),
        discord.Object(id=config_data['research_guild']),
    ])