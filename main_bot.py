import discord
from typing import List
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import os

token = 'MTAyMjQ1OTM3ODY0MjcyNjkyMg.GR8jli.H6DaCDDBrXwevENXoWF_jG0GCVBEwYZjIoqoxU'
intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)

class Abot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=1022461885162995722))
        self.synced = True
        print(f'Bot is online as {self.user}')

client = Abot()
tree = app_commands.CommandTree(client)

class AssessmentMenu(discord.ui.View):
    def __init__(self, embed=None):
        super().__init__()
        self.value = None
        self.embed = embed
    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e
        await interaction.response.edit_message(view=None, embed=self.embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(view=None, embed=None, content='*assessment cancelled*')


# adds new assessment
@tree.command(name='assessment', description='Adds new assessment', guild=discord.Object(id=1022461885162995722))
@app_commands.describe(ass_name = 'name of assessment')
@app_commands.describe(subject = 'subject of the assessment')
@app_commands.choices(ass_type = [
    Choice(name = 'Quiz', value = 'Quiz'),
    Choice(name = 'Discussion', value = 'Discussion'),
    Choice(name = 'Essay', value = 'Essay'),
    Choice(name = 'Team', value = 'Team'),
])
@app_commands.choices(category = [
    Choice(name = 'Enabling Assessment', value = 'EA'),
    Choice(name = 'Summative Assessment', value = 'SA'),
    Choice(name = 'Formative Assessment', value = 'FA'),
    Choice(name = 'Class Participation', value = 'CP'),
])
async def assessment(
    interaction: discord.Interaction, 
    ass_name: str, 
    subject: str,
    ass_type: str = None, 
    category: str = None, 
):
    # send prompt of new assessment
    embed=discord.Embed(title="New Assessment", description="details of your newly created assessment", color=0xff7800)
    embed.set_author(name=f"@{interaction.user}")
    embed.add_field(name="Assessment Name", value=ass_name, inline=False)
    embed.add_field(name="Due Date", value="10/15/2022", inline=True)
    embed.add_field(name="Type", value=ass_type, inline=True)
    embed.add_field(name="Category", value=category, inline=True)
    embed.add_field(name="Subject", value=subject, inline=False)


    # create custom ui view
    view = AssessmentMenu(embed=embed)

    # send the message to the server
    await interaction.response.send_message(embed=embed, view=view)

# dynamic options generator for subjects
@assessment.autocomplete('subject')
async def assessments_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    subjects = []
    return [
        Choice(name=subj, value=subj)
        for subj in subjects if current.lower() in subj.lower()
    ]    



client.run(token)