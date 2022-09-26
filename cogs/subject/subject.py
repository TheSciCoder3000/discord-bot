import discord
from typing import List
from configparser import ConfigParser
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice


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

        view = SubjectMenu(embed=embed)

        await interaction.response.send_message(embed=embed, view=view)


class SubjectMenu(discord.ui.View):
    def __init__(self, embed=None):
        super().__init__()
        self.value = None
        self.embed = embed
    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e
        await interaction.response.edit_message(view=None, embed=self.embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(view=None, embed=None, content='*subject cancelled*')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Subjects(bot), guilds=[
        discord.Object(id=config_data['test_guild']),
        discord.Object(id=config_data['tropa_guild'])
    ])