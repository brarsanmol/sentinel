import configparser
import os

import discord
import pugsql
from discord import app_commands

from sentinel.commands.verify import Verify


class Sentinel(discord.Client):
    def __init__(self, **options):
        super().__init__(loop=None, intents=discord.Intents().all())

        self.configuration = configparser.ConfigParser()
        self.configuration.read(os.path.join(os.path.dirname(__file__), "configuration.ini"))

        self.queries = pugsql.module(os.path.join(os.path.dirname(__file__), "queries"))
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        self.queries.connect(self.configuration.get("Database", "Url"))
        self.queries.create_tokens_table()

        self.tree.add_command(
            Verify(
                self.configuration.get("Email", "ApiKey"),
                self.configuration.get("Email", "Addresser"),
                self.queries,
            )
        )
        await self.tree.sync()
