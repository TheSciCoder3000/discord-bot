import discord
from db.manage import Connection, Subject, SubjectClass

class SubjectMenu(discord.ui.View):
    def __init__(self, embed=None, name=None, code=None):
        super().__init__()
        self.value = None
        self.name = name
        self.code = code
        self.embed = embed
    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e

        # connect to the database
        with Connection() as con:
            subject = Subject(name=self.name, code=self.code, guild_id=interaction.guild.id)
            # add new subject to the database
            con.add(subject)

            # add a new main class automatically
            SubjectClass(name="Main", subject=subject)


        await interaction.response.edit_message(view=None, embed=self.embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(view=None, embed=None, content='*subject cancelled*')