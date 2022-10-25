from typing import Union
from email.utils import parsedate
import discord
from dateutil.parser import parse
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from apscheduler.jobstores.base import JobLookupError
from cogs.utils import add_cogs_setup
from db.tables import DatePassed
from .menu import ChooseAssessmentDeleteMenu, PrivateReminderSettingsView, ReactionEventParser, SaveAssessmentMenu
from db.manage import Connection, Subject, Assessment, scheduler
import datetime


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
    async def add_assessment(
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

            async def save_callback(inter: discord.Interaction):
                con.add(assessment)
                assessment.dispatch_create_event(self.bot, inter.channel_id)

                message = await inter.original_response()

                embed.title = f"New Assessment #{assessment.id}"

                await message.edit(embed=embed)

                # add reactions
                await message.add_reaction('⏰')

            # create custom ui view
            view = SaveAssessmentMenu(save_callback, "Assessment creation cancelled", embed)

            # send the message to the server
            await interaction.response.send_message(embed=embed, view=view)
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        reaction = await ReactionEventParser(payload, self.bot, "New Assessment")
        assessment_id = reaction.embeds[0].title.replace("New Assessment #", '')

        with Connection() as con:
            assessment: Assessment = con.query(Assessment).get(assessment_id)
            if assessment is None:
                return

            name: str = assessment.name
            ass_job_id = f"{assessment_id} - {name}"
        
            if not reaction.is_valid():
                return

            try:
                # if clock emoji
                if str(reaction.emoji) == '⏰':
                    embed = reaction.embeds[0]

                    dm_msg = await reaction.dm_send(embed=embed)

                    await dm_msg.add_reaction('1️⃣')
                    await dm_msg.add_reaction('5️⃣')
                    await dm_msg.add_reaction('🔟')
                    await dm_msg.add_reaction('⚙️')
                
                # else if "1" emoji
                elif str(reaction.emoji) == '1️⃣':
                    assessment.dispatch_create_event(
                        self.bot, 
                        user_id=reaction.user_id, 
                        job_id=f"{ass_job_id} - 1 - {reaction.user_id}",
                        hour=1
                    )
                elif str(reaction.emoji) == '5️⃣':
                    assessment.dispatch_create_event(
                        self.bot, 
                        user_id=reaction.user_id, 
                        job_id=f"{ass_job_id} - 5 - {reaction.user_id}",
                        hour=5
                    )
                elif str(reaction.emoji) == '🔟':
                    assessment.dispatch_create_event(
                        self.bot, 
                        user_id=reaction.user_id, 
                        job_id=f"{ass_job_id} - 10 - {reaction.user_id}",
                        hour=10
                    )
                elif str(reaction.emoji) == '⚙️':
                    def on_submit(hour, min, sec):
                        submit_ass: Assessment = con.query(Assessment).get(assessment_id)
                        if submit_ass is None:
                            return print("Error: submit ass is none")
                        submit_ass.dispatch_create_event(
                            self.bot, 
                            user_id=reaction.user_id, 
                            job_id=f"{ass_job_id} - c - {reaction.user_id}",
                            hour=hour,
                            min=min,
                            sec=sec
                        )

                    view = PrivateReminderSettingsView(on_submit)

                    embed=discord.Embed(title="Do you want to custom set reminder intervals?")

                    await reaction.dm_send(embed=embed, view=view)
            except DatePassed:
                await reaction.dm_send("Error: unable to set reminder because it's passed")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        reaction = await ReactionEventParser(payload, self.bot, "New Assessment")
        assessment_id = reaction.embeds[0].title.replace("New Assessment #", '')

        with Connection() as con:
            assessment: Assessment = con.query(Assessment).get(assessment_id)
            if assessment is None:
                return

            name: str = assessment.name
            ass_job_id = f"{assessment_id} - {name}"

            if not reaction.is_valid():
                return

            # if removed emoji is "1"
            if str(reaction.emoji) == '1️⃣':
                assessment.dispatch_remove_event(
                    self.bot, 
                    job_id=f"{ass_job_id} - 1 - {reaction.user_id}",
                    user_id=reaction.user_id
                )
            elif str(reaction.emoji) == '5️⃣':
                assessment.dispatch_remove_event(
                    self.bot, 
                    job_id=f"{ass_job_id} - 5 - {reaction.user_id}",
                    user_id=reaction.user_id
                )
            elif str(reaction.emoji) == '🔟':
                assessment.dispatch_remove_event(
                    self.bot, 
                    job_id=f"{ass_job_id} - 10 - {reaction.user_id}",
                    user_id=reaction.user_id
                )
            elif str(reaction.emoji) == '⚙️':
                assessment.dispatch_remove_event(
                    self.bot, 
                    job_id=f"{ass_job_id} - c - {reaction.user_id}",
                    user_id=reaction.user_id
                )


    # dynamic options generator for subjects
    @add_assessment.autocomplete('subject')
    async def add_ass_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        with Connection() as con:
            subjects = [ass for ass in con.query(Subject).filter_by(guild_id=interaction.guild.id).all()]
            subj_names = [subj.name for subj in subjects]
            print(subj_names)
        
        return [
            Choice(name=subj.name, value=subj.id)
            for subj in subjects
            if current.lower() in subj.name.lower()
        ]
    

    @app_commands.command(name='remove-assessments', description='remove previous assessments')
    async def remove_assessments(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            subject: Union[Subject, None] = con.query(Subject).get(subject_id)

            if subject is None:
                return await interaction.response.send_message('Error: subject cannot be found')

            if len(subject.assessments) == 0:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title=f"Unable to fetch assessments of subject \"{subject.name}\"",
                        description=f"The subject \"{subject.name}\" has 0 assessments",
                        color=0x57e389
                    )
                )

            embed = discord.Embed(
                title="Delete Assessment Selection", 
                description=f"Please choose an assessment from `{subject.name}` to be deleted", 
                color=0xff7800
            )
            
            view = ChooseAssessmentDeleteMenu(self.bot, interaction.guild.id, subject.assessments, embed)
            
            await interaction.response.send_message(embed=embed, view=view)


    @commands.Cog.listener()
    async def on_remove_assessment(self, job_id: str, channel_id: int = None, user_id: int = None):
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            return print("Unable to find and remove job from database")

        # if global assessment is being deleted
        if user_id is None:
            # remove each individual user reminder
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job_id in job.id:
                    print(f'user id: "{job.id.replace(f"{job_id} - ", "")}"')
                    scheduler.remove_job(job.id)
                    indiv_user_id = int(job.id.replace(f"{job_id} - ", "")[4:])
                    indiv_user = await self.bot.fetch_user(indiv_user_id)
                    await indiv_user.send(f"The parent assessment has been deleted, you will no longer be getting a reminder from the assessment \"{job.id}\"")
        
            channel = await self.bot.fetch_channel(channel_id)
            await channel.send("successfully removed assessment reminder")
        else:
            user = await self.bot.fetch_user(user_id)
            await user.send("successfully unsubscribed to reminder")


    @remove_assessments.autocomplete('subject_id')
    async def remove_ass_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        subjects = []
        with Connection() as con:
            subjects = [ass for ass in con.query(Subject).filter_by(guild_id=interaction.guild.id).all()]
        
        return [
            Choice(name=subj.name, value=subj.id)
            for subj in subjects 
            if current.lower() in subj.name.lower()
        ]
    

    @app_commands.command(name="list-assessments")
    @app_commands.rename(subject_id="subject")
    async def list_assessments(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            subject: Subject = con.query(Subject).get(subject_id)
            assessments: list[Assessment] = subject.assessments

            if len(assessments) == 0:
                return await interaction.response.send_message(f"Subject `{subject.name}` has no assessments")

            embed=discord.Embed(title="List of Assessments", description=f"displays a list of assessments for {subject.name}")

            name_list = ""
            for ass in assessments:
                name_list += f"{ass.name}  -  {ass.category}\n"

            embed.add_field(name="Name", value=name_list)

            await interaction.response.send_message(embed=embed)
    

    @list_assessments.autocomplete('subject_id')
    async def list_ass_autocomplete(self, interaction: discord.Interaction, current: str):
        subjects = []
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
                and subj.guild_id == interaction.guild.id
            ]

        return subjects


async def setup(bot: commands.Bot) -> None:
    await add_cogs_setup(bot, Assessments(bot))