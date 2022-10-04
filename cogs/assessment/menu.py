import discord
from typing import Type
from db.manage import Connection, Subject, Assessment
from cogs.utils import SaveActionUi
from discord.ext import commands

SaveAssessmentMenu = SaveActionUi

async def ReactionEventParser(payload: discord.RawReactionActionEvent, bot: commands.Bot, valid_title: str):
    reaction = ReactionEvent(payload, bot, valid_title)
    await reaction._init()
    return reaction

class ReactionEvent:
    def __init__(self, payload: discord.RawReactionActionEvent, bot: commands.Bot, valid_title: str) -> None:
        self.bot = bot
        self.payload = payload

        # default payload attributes
        self.type = payload.event_type
        self.channel_id = payload.channel_id
        self.emoji = payload.emoji
        self.guild_id = payload.guild_id
        self.member = payload.member
        self.message_id = payload.message_id
        self.user_id = payload.user_id
        self.valid_title = valid_title

        self.dm = payload.member is None        # checks if the event is in server or dm

    async def _init(self):
        self.user = self.payload.member if not self.dm else await self.bot.fetch_user(self.payload.user_id)
        self.message: discord.Message
        try:
            channel = self.bot.get_channel(self.payload.channel_id)
            self.message = await channel.fetch_message(self.payload.message_id)
        except AttributeError:
            self.message = await self.user.fetch_message(self.payload.message_id)

        self.embeds = self.message.embeds

    
    async def dm_send(self, content = "", embed=None, view=None) -> discord.Message:
        return await self.user.send(content=content, embed=embed, view=view)
    
    def is_valid(self) -> bool:
        if len(self.embeds) == 0 or self.bot.user.id == self.user.id:
            return False

        if not self.valid_title in self.embeds[0].title:
            return False

        return True

class ChooseAssessmentDeleteMenu(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild_id: int, embed: discord.Embed = None):
        super().__init__()
        self.embed = embed
        self.bot = bot

        with Connection() as con:
            assessments: list[Assessment] = con.query(Assessment).filter_by(guild_id=guild_id).all()
            
            self.select = discord.ui.Select(
                placeholder="choose an assessment to be deleted",
                options=[
                    discord.SelectOption(label=ass.name, value=ass.id)
                    for ass in assessments
                ],
                row=1
            )
            self.select.callback = self.select_callback
            self.add_item(self.select)
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, row=2)
    async def cancel_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.title = "Deletion Cancelled"
        self.embed.description = "Assessment deletion has been cancelled"
        await interaction.response.edit_message(view=None, embed=self.embed)

    async def select_callback(self, interaction: discord.Interaction):
        ass_id = self.select.values[0]


        with Connection() as con:
            assessment: Assessment = con.query(Assessment).get(ass_id)
            
            self.embed.title = "Assessment Deletion Confirmation"
            self.embed.description = f"Are you sure you want to delete `{assessment.name}`"

            def delete_callback():
                assessment.dispatch_remove_event(
                    self.bot, f"{assessment.id} - {assessment.name}", 
                    interaction.channel_id
                )
                con.remove(assessment)

            view = ConfirmDeleteAssessment(assessment, delete_callback, self.embed)

            await interaction.response.edit_message(view=view, embed=self.embed)

class EditAssessmentMenu(discord.ui.View):
    def __init__(self, embed=None):
        super().__init__()
        self.value = None
        self.embed = embed

        self.type_options = ['Quiz', 'Discussion', 'Essay', 'Team',]
        self.cat_options = ['Enabling Assessment', 'Summative Assessment', 'Formative Assessment', 'Class Participation']

    @discord.ui.button(label="Name", style=discord.ButtonStyle.blurple)
    async def edit_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Subject", style=discord.ButtonStyle.blurple)
    async def subj_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Type", style=discord.ButtonStyle.blurple)
    async def type_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        select = discord.ui.Select(
            placeholder="Choose a new assessment type",
            options=[discord.SelectOption(label=opt) for opt in self.type_options]
        )

        async def parser(interaction: discord.Interaction):
            await self.select_callback(2, interaction, select.values[0])
        select.callback = parser

        view = CancelDetailMenu(self.embed)
        view.add_item(select)

        await interaction.response.send_message(embed=self.embed, view=view)

    @discord.ui.button(label="Category", style=discord.ButtonStyle.blurple)
    async def cat_name(self, interaction: discord.Interaction, button: discord.ui.Button):
        select = discord.ui.Select(
            placeholder="Choose a new assessment type",
            options=[discord.SelectOption(
                label=opt,
                value=f"{opt.split(' ')[0][0]}{opt.split(' ')[1][0]}"
            ) for opt in self.cat_options]
        )

        async def parser(interaction: discord.Interaction):
            await self.select_callback(3, interaction, select.values[0])
        select.callback = parser

        view = CancelDetailMenu(self.embed)
        view.add_item(select)

        await interaction.response.send_message(embed=self.embed, view=view)

    async def select_callback(self, pos: int, interaction: discord.Interaction, value: str):
        self.embed.set_field_at(pos, name="Type", value=value, inline=True)
        await interaction.response.edit_message(embed=self.embed, view=SaveAssessmentMenu(embed=self.embed))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_edit_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=SaveAssessmentMenu(self.embed))

    # TODO: add button for editing time and date


class CancelDetailMenu(discord.ui.View):
    def __init__(self, embed=None):
        super().__init__()
        self.value = None
        self.embed = embed

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.grey)
    async def cancel_edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.embed, view=EditAssessmentMenu(self.embed))



class ConfirmDeleteAssessment(discord.ui.View):
    def __init__(self, assessment, delete_callback, embed=None):
        super().__init__()
        self.assessment = assessment
        self.delete_cb = delete_callback
        self.embed = embed

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_assessment_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed = discord.Embed(title="Delete Assessment Successful", description=f"Successfuly deleted assessemtn \"{self.assessment.name}\"", color=0x57e389)
        self.delete_cb()
        await interaction.response.edit_message(embed=self.embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_delete_assessment_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed = discord.Embed(title="Delete Assessment Cancellation", description=f"deletion of assessemtn \"{self.assessment.name}\" is cancelled", color=0x57e389)
        await interaction.response.edit_message(embed=self.embed, view=None)