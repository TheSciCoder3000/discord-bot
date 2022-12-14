import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from db.manage import Connection, Subject, Schedule, SubjectClass, scheduler
from dateutil.parser import parse
from cogs.utils import SaveActionUi, add_cogs_setup
from .schedMenu import ChooseSchedMenu, SelectDeleteSchedMenu


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
        # connect to the database
        with Connection() as con:
            # get the subject data and its classes
            subject_data = con.query(Subject).get(subject)

            if subject_data is None:
                await interaction.response.send_message(content="Error: subject does not exist")
                return

            class_data = subject_data.classes

            # create an embed
            embed=discord.Embed(title="New Schedule", description="details of your newly created schedule", color=0xff7800)
            embed.set_author(name=f"@{interaction.user}")
            embed.add_field(name="Day", value=self.dayList[day], inline=True)
            str_time_start = parse(time_in).strftime("%I:%M %p")
            str_time_end = parse(time_out).strftime("%I:%M %p")
            embed.add_field(name="Time", value=f"{str_time_start} - {str_time_end}", inline=True)

            # create schedule instance from parameters
            sched = Schedule(
                weekdays=day, 
                time_in=parse(time_in).time(), 
                time_out=parse(time_out).time(), 
                guild_id=interaction.guild.id
            )

            # if there is only one connected class to the subject
            if len(class_data) == 1:
                embed.insert_field_at(0, name="Subject", value=subject_data.code, inline=False)

                sched_check = con.query(Schedule).filter_by(
                    time_in=sched.time_in,
                    time_out=sched.time_out,
                    weekdays=sched.weekdays,
                    sched_class=class_data[0]
                ).all()

                if len(sched_check) > 0:
                    return await interaction.response.send_message("Error: schedule aready exists")

                async def save_callback(inter: discord.Interaction):
                    # set the sched instance's sched column
                    sched.sched_class = class_data[0]
                    con.add(sched)
                    sched.dispatch_sched_event(self.bot, interaction.channel_id)

                view = SaveActionUi(save_callback, '*schedule cancelled*', embed=embed)

                # send confirmation prompt
                await interaction.response.send_message(embed=embed, view=view)

            else:
                # create a select ui
                select = discord.ui.Select(
                    placeholder="Choose one of the available classes",
                    options=[
                        discord.SelectOption(
                            label=subj_class.name,
                            value=subj_class.id
                        ) for subj_class in class_data
                    ]
                )

                view = ChooseSchedMenu(sched, select, con, self.bot, embed)

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
                and subj.guild_id == interaction.guild.id
            ]

        return subjects


    @app_commands.command(name="remove-sched", description="removes a schedule from a class")
    @app_commands.rename(subject_id='subject')
    async def remove_sched(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            delete_subject = con.query(Subject).get(subject_id)
            
            if delete_subject is None:
                return await interaction.response.send_message("Error: subject does not exist")
            
            select = discord.ui.Select(
                placeholder="Select one among of the classes",
                options=[discord.SelectOption(label=subject_class.name, value=subject_class.id) for subject_class in delete_subject.classes]
            )

            embed = discord.Embed(
                title="Remove Class", 
                description=f"Please select one of the classes of subject \"{delete_subject.name}\"", 
                color=0xff7800
            )

            view = SelectDeleteSchedMenu(con, delete_subject, self.bot, embed)

            await interaction.response.send_message(embed=embed, view=view)


    @commands.Cog.listener()
    async def on_remove_schedule(self, sched_id: str, channel_id: int):
        scheduler.remove_job(sched_id)
        channel = self.bot.get_channel(channel_id)
        await channel.send("selected schedule has been removed")


    @remove_sched.autocomplete('subject_id')
    async def remove_sched_autocomplete(self, interaction: discord.Interaction, current: str):
        subjects = []
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
                and subj.guild_id == interaction.guild.id
            ]

        return subjects


    @app_commands.command(name='ping')
    async def ping_bot(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")
        message = await interaction.original_response()
        print(f'created at {message.created_at.strftime("%I:%M %p")}')


    @app_commands.command(name="list-schedules", description="List down all the schedules in a particular subject")
    @app_commands.rename(subject_id="subject")
    async def list_schedules(self, interaction: discord.Interaction, subject_id: int):
        with Connection() as con:
            subject: Subject = con.query(Subject).get(subject_id)

            if subject is None:
                return await interaction.response.send_message("Error: subject does not exist")

            classes: SubjectClass = subject.classes

            embeds: list[discord.Embed] = [None for _ in classes]
            for indx, class_inst in enumerate(classes):
                embeds[indx] = discord.Embed(
                    title=f"List of Schedules for Class: `{class_inst.name}`",
                    description=f"A list of all the schedules under the class \"{class_inst.name}\""
                )

                schedules: list[Schedule] = class_inst.schedules

                def sched_sorter(sched: Schedule):
                    day_indx = sched.days.index(sched.get_day())
                    return day_indx, sched.time_in

                sorted_schedules: list[Schedule] = sorted(schedules, key=sched_sorter)

                sched_str_list = ""
                initial_day = None
                for sched in sorted_schedules:
                    if initial_day is None:
                        initial_day = sched.get_day()
                    elif initial_day != sched.get_day():
                        sched_str_list += "\n"
                        initial_day = sched.get_day()
                    sched_str_list += f"{sched}\n"

                embeds[indx].add_field(name="Name", value=sched_str_list if len(schedules) != 0 else "No schedules")

            await interaction.response.send_message(embeds=embeds)
    

    @list_schedules.autocomplete('subject_id')
    async def list_sched_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        subjects = []
        with Connection() as con:
            subjects = [
                Choice(name=f"{subj.name}", value=subj.id)
                for subj in con.query(Subject) if current.lower() in subj.name.lower()
                and subj.guild_id == interaction.guild.id
            ]

        return subjects



async def setup(bot: commands.Bot) -> None:
    await add_cogs_setup(bot, Schedules(bot))