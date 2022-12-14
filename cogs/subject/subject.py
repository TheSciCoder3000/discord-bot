import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.utils import DeleteActionUi, add_cogs_setup
from db.manage import Connection, Subject, SubjectClass
from .subjMenu import SubjectMenu


class Subjects(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='add-subject', description="add a new subject")
    async def add_subject(
        self,
        interaction: discord.Interaction,
        name: str,
        code: str
    ):
        # check if subject already exists
        exist_subjs = None
        with Connection() as con:
            exist_subjs = con.query(Subject).filter_by(code=code, guild_id=interaction.guild.id).first()

        if not exist_subjs is None:
            return await interaction.response.send_message(f'*Error: Subject code `{code}` already exists*')
        
        # create prompt of new assessment
        embed=discord.Embed(title="New Subject", description="details of your newly created subject", color=0xff7800)
        embed.set_author(name=f"@{interaction.user}")
        embed.add_field(name="Subject Name", value=name, inline=False)
        embed.add_field(name="Subject Code", value=code, inline=True)

        async def save_callback(interaction: discord.Interaction):
            with Connection() as con:
                subject = Subject(name=name, code=code, guild_id=interaction.guild.id)
                # add new subject to the database
                con.add(subject)

                # add a new main class automatically
                SubjectClass(name="Main", subject=subject)

        view = SubjectMenu(save_callback, "Subject Creation cancelled", embed=embed)
            
        await interaction.response.send_message(embed=embed, view=view)

        timed_out = await view.wait()

        if timed_out and not view.saved:
                message = await interaction.original_response()
                await message.edit(embed = discord.Embed(
                    title="Subject Creation Expired",
                    description="Your subject creation has timedout and expired. Please create another one",
                    color=0xed333b
                ), view=view.clear_items())

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
            subjects: list[Subject] = con.query(Subject).filter_by(guild_id=interaction.guild.id).all()

            name_list: str = ""
            code_list: str = ""
            for subj in subjects:
                name_list += f"`{subj.name}`\n"
                code_list += f"`{subj.code}`\n"

            embed=discord.Embed(title="List of Subjects", description="list of all server subjects")
            embed.add_field(name="Name", value=name_list)
            embed.add_field(name="Code", value=code_list)



        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await add_cogs_setup(bot, Subjects(bot))