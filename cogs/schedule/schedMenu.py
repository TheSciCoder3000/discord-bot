import discord
from db.manage import Connection, Subject, SubjectClass


class ScheduleSaveMenu(discord.ui.View):
    def __init__(self, schedule, embed):
        super().__init__()
        self.value = None
        self.schedule = schedule
        self.embed = embed

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_sched(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e

        with Connection() as con:
            con.add(self.schedule)

        await interaction.response.edit_message(embed=self.embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_sched(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(embed=self.embed, view=None)


class ChooseSchedMenu(discord.ui.View):
    def __init__(self, schedule, select, embed):
        super().__init__()
        self.value = None
        self.schedule = schedule
        self.embed = embed

        async def parser(interaction: discord.Interaction):
            await self.select_callback(interaction, select.values[0])

        select.callback = parser
        self.add_item(select)

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.grey)
    async def cancel_save_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=None, view=None, content='*schedule cancelled*')

    async def select_callback(self, interaction: discord.Interaction, class_id: int):
        # connect to the database
        with Connection() as con:
            # fetch class item using class id parameter
            class_inst = con.query(SubjectClass).filter_by(id=class_id).first()

            # link schedule to its class item
            self.schedule.sched_class = class_inst

            # modify embed
            self.embed.insert_field_at(0, name="Subject", value=class_inst.subject.name, inline=False)
            self.embed.add_field(name="Class", value=class_inst.name, inline=True)

            view = ScheduleSaveMenu(self.schedule, self.embed)

            await interaction.response.edit_message(embed=self.embed, view=view)