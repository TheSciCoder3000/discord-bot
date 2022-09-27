import discord
from configparser import ConfigParser
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from db.manage import Connection, Subject, SubjectClass
from cogs.utils import SaveActionUi


config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']


class Classes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add-class", description="add a new class for a subject")
    @app_commands.describe(name="name of the class")
    @app_commands.describe(subject="subject of the class")
    async def add_class(self, interaction: discord.Interaction, name: str, subject: int):
        with Connection() as con:
            subject_inst = con.query(Subject).get(subject)

            if subject_inst is None:
                await interaction.response.send_message(content="Error: subject does not exist")
                return

            embed=discord.Embed(title="New Class", description="details of your newly created class", color=0xff7800)
            embed.set_author(name=f"@{interaction.user}")
            embed.add_field(name="Name", value=name, inline=False)
            embed.add_field(name="Subject", value=subject_inst.code, inline=False)

            def add_class_db():
                con.add(SubjectClass(
                    name=name,
                    subject=subject_inst
                ))

            view = SaveActionUi(add_class_db, "`*Class is cancelled*`", embed=embed)

            await interaction.response.send_message(embed=embed, view=view)

    @add_class.autocomplete('subject')
    async def add_class_autocomplete(self, interaction: discord.Interaction, current: str):
        subjects = []
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower() and subj.guild_id == interaction.guild.id
            ]

        return subjects


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Classes(bot), guilds=[
        discord.Object(id=config_data['test_guild']),
        discord.Object(id=config_data['tropa_guild']),
        discord.Object(id=config_data['research_guild']),
    ])