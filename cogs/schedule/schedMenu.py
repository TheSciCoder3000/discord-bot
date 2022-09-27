import discord
from db.manage import Connection, Subject, SubjectClass


class ChooseSchedMenu(discord.ui.View):
    def __init__(self, schedule, select, on_select, embed):
        super().__init__()
        self.value = None
        self.schedule = schedule
        self.embed = embed
        self.on_select = on_select

        async def parser(interaction: discord.Interaction):
            await self.select_callback(interaction, select.values[0])

        select.callback = parser
        self.add_item(select)

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.danger)
    async def cancel_save_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=None, view=None, content='*schedule cancelled*')

    async def select_callback(self, interaction: discord.Interaction, class_id: int):
        embed, view = self.on_select()

        await interaction.response.edit_message(embed=embed, view=view)