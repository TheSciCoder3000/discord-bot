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