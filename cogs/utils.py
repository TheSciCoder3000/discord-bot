import discord


class SaveActionUi(discord.ui.View):
    def __init__(self, save_callback, cancel_content, embed=None):
        super().__init__()
        self.value = None
        self.embed = embed
        self.save_callback = save_callback
        self.cancel_content = cancel_content

    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.embed is None:
            self.embed.color = 0x2ec27e
        
        self.save_callback()

        await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.embed is None:
            self.embed.color = 0xe01b24
        await interaction.response.edit_message(embed=self.embed, view=None, content=self.cancel_content)