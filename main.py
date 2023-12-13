import os

from dotenv import load_dotenv
import discord
from discord import app_commands

from typing import Optional, Any

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Specify the intents of the bot
intents = discord.Intents.all()
intents.dm_messages = True


class Aclient(discord.AutoShardedClient):
    def __init__(self):
        super().__init__(intents=intents, shard_count=1)
        self.added = False
        self.synced = False  # we use this so the bot doesn't sync commands more than once

    # commands local sync
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync()  # global (can take 1-24 hours)
            self.synced = True
        if not self.added:
            self.added = True
        # logger.info(f"We have logged in as {self.user}.")
        print(f'We have logged in as {self.user}.')


client = Aclient()
tree = app_commands.CommandTree(client)


class SelectView(discord.ui.View):
    def __init__(self, text, roles_number, interaction):
        super().__init__(timeout=None)
        self.mgs = text
        self.n_roles = roles_number
        self.interaction = interaction
        self.add_item(RolesSelect(text, roles_number, view=self))

    async def disable_one_item(self, select):
        for item in self.children:
            if item == select:
                item.disabled = True
        await self.interaction.edit_original_response(view=self)


class RolesSelect(discord.ui.RoleSelect):
    def __init__(self, text, roles_number, view):
        super().__init__(
            placeholder='Select Roles',
            max_values=roles_number,
            custom_id='roles_select'
        )
        self.text = text
        self.my_view = view

    async def callback(self, interaction: discord.Interaction):
        dmed_users = []
        for i in self.values:
            members = i.members
            for each in members:
                if each != client.user and each not in dmed_users:
                    await each.send(content=self.text)
                    dmed_users.append(each)
        await SelectView.disable_one_item(self=self.my_view, select=self)
        await interaction.response.send_message(content='All the dms have been sent', ephemeral=True)


@tree.command(name='send_dm', description='sends dms to roles or users')
async def send_dm(interaction: discord.Interaction, message: str):
    roles_number = len(interaction.guild.roles)
    view = SelectView(message, roles_number, interaction)
    await interaction.response.send_message(view=view, ephemeral=True)


client.run(DISCORD_TOKEN)
