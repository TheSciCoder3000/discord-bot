from typing import Union
import discord
from discord.ext import commands
from config import repl, test_guild, tropa_guild, research_guild

async def add_cogs_setup(bot: commands.Bot, CustomCog: commands.Cog):
    if repl: await bot.add_cog(CustomCog)
    else: await bot.add_cog(CustomCog, guilds=[
        discord.Object(id=test_guild),
        discord.Object(id=tropa_guild),
        discord.Object(id=research_guild),
    ])

class SaveActionUi(discord.ui.View):
    def __init__(self, save_callback, cancel_content: str, embed: Union[discord.Embed, None] = None, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None
        self.embed = embed
        self.save_callback = save_callback
        self.cancel_content = cancel_content
        self.saved = False

    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.embed is None:
            self.embed.color = 0x2ec27e

        self.saved = True
        
        await interaction.response.edit_message(embed=self.embed, view=None)

        await self.save_callback(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.embed is None:
            self.embed = discord.Embed(
                title=self.cancel_content,
                description="The process has been cancelled. You can try to create another one.",
                color=0xe01b24
            )

        await interaction.response.edit_message(embed=self.embed, view=None)

class DeleteActionUi(discord.ui.View):
    def __init__(self, delete_callback, deleted_content: str, cancelled_content: str):
        super().__init__()
        self.deleted_content = deleted_content
        self.cancelled_content = cancelled_content
        self.delete_callback = delete_callback
        
    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.delete_callback()
        await interaction.response.edit_message(embed=None, view=None, content=self.deleted_content)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=None, view=None, content=self.cancelled_content)