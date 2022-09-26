import discord
from typing import List
from configparser import ConfigParser
from discord import app_commands
from discord.ext import commands
from db.manage import Connection, Subject
from .subjMenu import SubjectMenu


config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']


class Subjects(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='add-subject', description="add a new subject")
    async def add_subject(
        self,
        interaction: discord.Interaction,
        subj_name: str,
        code: str
    ):
        # send prompt of new assessment
        embed=discord.Embed(title="New Subject", description="details of your newly created subject", color=0xff7800)
        embed.set_author(name=f"@{interaction.user}")
        embed.add_field(name="Subject Name", value=subj_name, inline=False)
        embed.add_field(name="Subject Code", value=code, inline=True)

        view = SubjectMenu(embed=embed, name=subj_name, code=code)

        exist_subjs = None
        with Connection() as con:
            exist_subjs = con.query(Subject).filter_by(code=code).first()

        if not exist_subjs is None:
            await interaction.response.send_message(f'*Error: Subject code `{code}` already exists*')
            return
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Subjects(bot), guilds=[
        discord.Object(id=config_data['test_guild']),
        discord.Object(id=config_data['tropa_guild']),
        discord.Object(id=config_data['research_guild']),
    ])