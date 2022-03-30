import configparser
import os

import discord
from discord import app_commands

from sentinel.commands.verify import Verify


class Sentinel(discord.Client):
    def __init__(self, **options):
        super().__init__(loop=None, intents=discord.Intents().all())

        self.configuration = configparser.ConfigParser()
        self.configuration.read(
            os.path.join(os.path.dirname(__file__), "configuration.ini")
        )

        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        self.tree.add_command(Verify())
        await self.tree.sync()
