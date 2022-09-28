from calendar import weekday
from typing import Union
import discord
from cogs.utils import DeleteActionUi, SaveActionUi
from db.manage import Connection, Subject, SubjectClass, Schedule


class ChooseSchedMenu(discord.ui.View):
    def __init__(self, schedule: Schedule, select: discord.ui.Select, connection: Connection, embed: discord.Embed):
        super().__init__()
        self.value = None
        self.schedule = schedule
        self.embed = embed
        self.connection = connection
        
        async def parser(interaction: discord.Interaction):
            await self.select_callback(interaction, select.values[0])

        select.callback = parser
        self.add_item(select)

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.danger)
    async def cancel_save_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=None, view=None, content='*schedule cancelled*')

    async def select_callback(self, interaction: discord.Interaction, class_id: int):
        class_inst = self.connection.query(SubjectClass).get(class_id)

        sched_inst = self.connection.query(Schedule).filter_by(
            time_in=self.schedule.time_in,
            time_out=self.schedule.time_out,
            weekdays=self.schedule.weekdays,
            sched_class=class_inst
        ).all()

        if len(sched_inst) > 0:
            return await interaction.response.edit_message("Error: schedule aready exists")

        self.embed.insert_field_at(0, name="Subject", value=class_inst.subject.name, inline=False)
        self.embed.add_field(name="Class", value=class_inst.name, inline=True)

        def save_callback():
            self.schedule.sched_class = class_inst
            self.connection.add(self.schedule)

        view = SaveActionUi(save_callback, '*schedule cancelled*', embed=self.embed)

        await interaction.response.edit_message(embed=self.embed, view=view)


class SelectDeleteSchedMenu(discord.ui.View):
    def __init__(self, connection: Connection, subject: Subject, embed):
        super().__init__()
        self.connection = connection
        self.subj_class: Union[SubjectClass, None] = None
        self.subject = subject
        self.embed = embed
        self.select = discord.ui.Select(
            placeholder="Select one of the classes",
            options=[
                discord.SelectOption(label=subj_class.name, value=subj_class.id)
                for subj_class in subject.classes
            ]
        )

        self.select.callback = self.select_class_callback
        self.add_item(self.select)
    
    async def select_class_callback(self, interaction: discord.Interaction):
        class_id = self.select.values[0]
        self.subj_class = self.connection.query(SubjectClass).get(class_id)
        self.embed = discord.Embed(title="Removing Schedule", description="Please choose a schedule", color=0xff7800)

        self.remove_item(self.select)

        self.select = discord.ui.Select(
            placeholder="Select a schedule to be deleted",
            options=[
                discord.SelectOption(label=str(sched), value=sched.id)
                for sched in self.subj_class.schedules
            ]
        )

        self.select.callback = self.select_sched_callback
        self.add_item(self.select)

        await interaction.response.edit_message(embed=self.embed, view=self)

    async def select_sched_callback(self, interaction: discord.Interaction):
        sched_id = self.select.values[0]
        sched = self.connection.query(Schedule).get(sched_id)

        self.embed = discord.Embed(
            title="Are you sure you want to delete this sched?",
            description=f"Are you sure you want to delete this schedule at `{str(sched)}` in the subject `{self.subject.name}`",
            color=0xff7800    
        )

        def delete_callback():
            self.connection.remove(sched)

        view = DeleteActionUi(delete_callback, f"Schedule `{str(sched)}` has been removed", "schedule deletion cancelled")

        await interaction.response.edit_message(view=view, embed=self.embed)