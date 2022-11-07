import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.classes.classMenu import DeleteClassSelect, SaveClassMenu
from db.manage import Connection, Subject, SubjectClass
from cogs.utils import add_cogs_setup


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

            async def add_class_db(inter: discord.Interaction):
                con.add(SubjectClass(
                    name=name,
                    subject=subject_inst
                ))

            view = SaveClassMenu(add_class_db, "Class creation is cancelled", embed=embed)

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

    @app_commands.command(name="remove-class", description="removes the class and its schedules")
    @app_commands.rename(subject_id="subject")
    async def remove_class(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            delete_subject = con.query(Subject).get(subject_id)
            
            if delete_subject is None:
                return await interaction.response.send_message("Error: subject does not exist")

            if len(delete_subject.classes) == 1:
                return await interaction.response.send_message(
                    f"Error: the subject `{delete_subject.name}` has only one class, `{delete_subject.classes[0].name}`, A subject should always contain one class"
                )
            
            select = discord.ui.Select(
                placeholder="Select one among of the classes",
                options=[discord.SelectOption(label=subject_class.name, value=subject_class.id) for subject_class in delete_subject.classes]
            )

            embed = discord.Embed(
                title="Remove Class", 
                description=f"Please select one of the classes of subject \"{delete_subject.name}\"", 
                color=0xff7800
            )

            view = DeleteClassSelect(con, select, embed)

            await interaction.response.send_message(view=view, embed=embed)
    
    @remove_class.autocomplete('subject_id')
    async def remove_class_autocomplete(self, interaction: discord.Interaction, current: str):
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
                and subj.guild_id == interaction.guild.id
            ]

        return subjects


async def setup(bot: commands.Bot) -> None:
    await add_cogs_setup(bot, Classes(bot))