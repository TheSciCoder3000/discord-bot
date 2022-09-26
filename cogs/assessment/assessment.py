import discord
from configparser import ConfigParser
from typing import List
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from .menu import SaveAssessmentMenu
import os

config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']


class Assessments(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='add-assessment', description='Adds new assessment')
    @app_commands.describe(ass_name = 'name of assessment')
    @app_commands.describe(subject = 'subject of the assessment')
    @app_commands.choices(ass_type = [
        Choice(name = 'Quiz', value = 'Quiz'),
        Choice(name = 'Discussion', value = 'Discussion'),
        Choice(name = 'Essay', value = 'Essay'),
        Choice(name = 'Team', value = 'Team'),
    ])
    @app_commands.choices(category = [
        Choice(name = 'Enabling Assessment', value = 'EA'),
        Choice(name = 'Summative Assessment', value = 'SA'),
        Choice(name = 'Formative Assessment', value = 'FA'),
        Choice(name = 'Class Participation', value = 'CP'),
    ])
    async def assessment(
        self,
        interaction: discord.Interaction, 
        ass_name: str, 
        subject: str,
        ass_type: str = None, 
        category: str = None, 
    ):
        # send prompt of new assessment
        embed=discord.Embed(title="New Assessment", description="details of your newly created assessment", color=0xff7800)
        embed.set_author(name=f"@{interaction.user}")
        embed.add_field(name="Assessment Name", value=ass_name, inline=False)
        embed.add_field(name="Due Date", value="10/15/2022", inline=True)
        embed.add_field(name="Type", value=ass_type, inline=True)
        embed.add_field(name="Category", value=category, inline=True)
        embed.add_field(name="Subject", value=subject, inline=False)


        # create custom ui view
        view = SaveAssessmentMenu(embed=embed)

        # send the message to the server
        await interaction.response.send_message(embed=embed, view=view)


    # dynamic options generator for subjects
    @assessment.autocomplete('subject')
    async def assessments_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        # TODO: connect to database
        subjects = []
        return [
            Choice(name=subj, value=subj)
            for subj in subjects if current.lower() in subj.lower()
        ]    


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Assessments(bot), guilds=[
        discord.Object(id=config_data['test_guild']),
        discord.Object(id=config_data['tropa_guild'])
    ])