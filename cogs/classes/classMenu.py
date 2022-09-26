import discord
from db.manage import Connection, SubjectClass


class SaveClassMenu(discord.ui.View):
    def __init__(self, class_inst, embed):
        super().__init__()
        self.value = None
        self.class_inst = class_inst
        self.embed = embed

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_class(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e

        with Connection() as con:
            con.add(self.class_inst)

            await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_save_class(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(embed=self.embed, view=None)
