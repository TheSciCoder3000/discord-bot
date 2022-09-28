import discord
from typing import Union
from cogs.utils import DeleteActionUi
from db.manage import Connection, SubjectClass


class SaveClassMenu(discord.ui.View):
    def __init__(self, class_inst: SubjectClass, embed: Union[discord.Embed, None]):
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


class DeleteClassSelect(discord.ui.View):
    def __init__(self, connection: Connection, select: discord.ui.Select, embed: Union[discord.Embed, None]):
        super().__init__()
        self.connection = connection
        self.embed = embed
        self.select = select

        self.select.callback = self.select_callback
        self.add_item(self.select)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None, embed=None, content="Class deletion cancelled")

    async def select_callback(self, interaction: discord.Interaction):
        delete_class = self.connection.query(SubjectClass).get(self.select.values[0])
        self.embed = discord.Embed(
            title="Remove Class", 
            description=f"Are you sure you want to delete your class, \"{delete_class.name}\" from the subject \"{delete_class.subject.name}\"?", 
            color=0xff7800
        )

        def delete_callback():
            self.connection.remove(delete_class)

        view = DeleteActionUi(delete_callback, f"class `{delete_class.name}` has been deleted", "class deletion cancelled")

        await interaction.response.edit_message(view=view, embed=self.embed)