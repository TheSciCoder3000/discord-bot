import discord
from typing import Type
from db.manage import Connection, Subject, Assessment
from cogs.utils import SaveActionUi

SaveAssessmentMenu = SaveActionUi

class SaveAssessmentMenuBeta(discord.ui.View):
    def __init__(self, assessment_data, embed=None):
        super().__init__()
        self.assessment = assessment_data
        self.value = None
        self.embed = embed
    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0x2ec27e
        with Connection() as con:
            con.add(self.assessment)
        await interaction.response.edit_message(view=None, embed=self.embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = 0xe01b24
        await interaction.response.edit_message(view=None, embed=None, content='*assessment cancelled*')

    # @discord.ui.button(label="Edit", style=discord.ButtonStyle.grey)
    # async def edit_assessment(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.edit_message(view=EditAssessmentMenu(self.embed))


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