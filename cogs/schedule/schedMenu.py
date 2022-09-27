import discord
from cogs.utils import SaveActionUi
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
        self.embed.insert_field_at(0, name="Subject", value=class_inst.subject.name, inline=False)
        self.embed.add_field(name="Class", value=class_inst.name, inline=True)

        def save_callback():
            self.schedule.sched_class = class_inst
            self.connection.add(self.schedule)

        view = SaveActionUi(save_callback, '*schedule cancelled*', embed=self.embed)

        await interaction.response.edit_message(embed=self.embed, view=view)