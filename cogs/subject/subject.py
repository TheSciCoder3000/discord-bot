import discord
from typing import List
from configparser import ConfigParser
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.utils import DeleteActionUi
from db.manage import Connection, Subject
from db.tables import SubjectClass
from .subjMenu import SubjectMenu
from config import test_guild, tropa_guild, research_guild


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
            exist_subjs = con.query(Subject).filter_by(code=code, guild_id=interaction.guild.id).first()

        if not exist_subjs is None:
            await interaction.response.send_message(f'*Error: Subject code `{code}` already exists*')
            return
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="remove-subject", description="remove a subject and all its related classes, schedules and assessments")
    @app_commands.rename(subject_id='subject')
    async def remove_subject(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            delete_subject = con.query(Subject).get(subject_id)
            del_classes = delete_subject.classes
            sched_count = 0
            for del_class in del_classes:
                sched_count += len(del_class.schedules)

            if delete_subject is None:
                await interaction.response.send_message("Error: subject does not exist")
                return

            embed = discord.Embed(
                title="Remove Subject", 
                description=f"Are you sure you want to delete your subject, \"{delete_subject.name}\"?", 
                color=0xff7800
            )

            embed.set_footer(text=f"\nYou will also be deleting the following:\nClasses ({len(del_classes)})\nSchedules ({sched_count})")
            
            def delete_callback():
                con.remove(delete_subject)

            view = DeleteActionUi(delete_callback, f"\"{delete_subject.name}\" has been deleted", "subject deletion cancelled")
            
            await interaction.response.send_message(embed=embed, view=view)
    
    @remove_subject.autocomplete('subject_id')
    async def remove_subject_autocomplete(self, interaction: discord.Interaction, current: str):
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
                and subj.guild_id == interaction.guild.id
            ]

        return subjects


    @app_commands.command(name="list-subjects")
    async def list_subjects(self, interaction: discord.Interaction):
        with Connection() as con:
            subjects: list[Subject] = con.query(Subject).all()

            name_list: str = ""
            code_list: str = ""
            for subj in con.query(Subject).all():
                name_list += f"`{subj.name}`\n"
                code_list += f"`{subj.code}`\n"

            embed=discord.Embed(title="List of Subjects", description="list of all server subjects")
            embed.add_field(name="Name", value=name_list)
            embed.add_field(name="Code", value=code_list)



        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Subjects(bot), guilds=[
        discord.Object(id=test_guild),
        discord.Object(id=tropa_guild),
        discord.Object(id=research_guild),
    ])