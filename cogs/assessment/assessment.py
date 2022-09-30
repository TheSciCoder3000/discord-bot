from email.utils import parsedate
import discord
from dateutil.parser import parse
from typing import List
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from .menu import SaveAssessmentMenu, ConfirmDeleteAssessment
from db.manage import Connection, Subject, Assessment, scheduler
from config import test_guild, research_guild, tropa_guild


class Assessments(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='add-assessment', description='Adds new assessment')
    @app_commands.rename(ass_name="name", ass_type="type", due_date="date")
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
        subject: int,
        due_date: str,
        due_time: str = None,
        ass_type: str = None, 
        category: str = None, 
    ):
        # get subject db instance
        subject_data = None
        with Connection() as con:
            subject_data = con.query(Subject).filter_by(id=subject).first()
            parsed_date = parse(due_date)
            parsed_time = None if due_time is None else parse(due_time).time()

            # create prompt of new assessment
            embed=discord.Embed(title="New Assessment", description="details of your newly created assessment", color=0xff7800)
            embed.set_author(name=f"@{interaction.user}")
            embed.add_field(name="Assessment Name", value=ass_name, inline=False)
            embed.add_field(name="Due Date", value=parsed_date.strftime("%m/%d/%Y"), inline=True)
            embed.add_field(name="Time", value="Whole day" if parsed_time is None else parsed_time.strftime("%I:%M %p"), inline=True)
            embed.add_field(name="Type", value=ass_type, inline=True)
            embed.add_field(name="Category", value=category, inline=True)
            embed.add_field(name="Subject", value=subject_data.code, inline=False)

            # create new assessment db instance
            assessment = Assessment(
                name=ass_name, 
                subject=subject_data,
                due_date=parsed_date,
                time=parsed_time,
                ass_type=ass_type, 
                category=category, 
                guild_id=interaction.guild.id
            )

            def save_callback():
                con.add(assessment)
                assessment.dispatch_create_event(self.bot, interaction.channel_id)

            # create custom ui view
            view = SaveAssessmentMenu(save_callback, "Assessment creation cancelled", embed)

            # send the message to the server
            await interaction.response.send_message(embed=embed, view=view)


    # dynamic options generator for subjects
    @assessment.autocomplete('subject')
    async def assessments_autocomplete(
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
    

    @app_commands.command(name='remove-assessments', description='remove previous assessments')
    async def remove_assessments(self, interaction: discord.Interaction, ass_id: int):
        with Connection() as con:
            ass_to_delete = con.query(Assessment).filter_by(id=ass_id).first()

            if ass_to_delete is None:
                await interaction.response.send_message('Error: assessment cannot be found')
                return

            embed = discord.Embed(title="Delete Assessment Confirmation", description=f"Are you sure you want to delete {ass_to_delete.name}?", color=0xff7800)
            
            def delete_callback():
                con.remove(ass_to_delete)
            
            view = ConfirmDeleteAssessment(ass_to_delete, delete_callback)
            
            await interaction.response.send_message(embed=embed, view=view)


    @remove_assessments.autocomplete('ass_id')
    async def remove_ass_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        assessments = []
        with Connection() as con:
            assessments = [ass for ass in con.query(Assessment).all()]
        
        return [
            Choice(name=f"{ass.name} - {ass.subject.code}", value=ass.id)
            for ass in assessments if current.lower() in f"{ass.name} - {ass.subject.code}".lower()
        ]


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Assessments(bot), guilds=[
        discord.Object(id=test_guild),
        discord.Object(id=tropa_guild),
        discord.Object(id=research_guild),
    ])