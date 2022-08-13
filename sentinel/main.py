import configparser
import os

import discord
import pugsql
from discord import Member, app_commands

from sentinel.commands.code import Code
from sentinel.commands.verify import Verify


class Sentinel(discord.Client):
    def __init__(self, **options):
        super().__init__(loop=None, intents=discord.Intents().all())

        self.configuration = configparser.ConfigParser()

        if os.path.isfile(os.path.join(os.path.dirname(__file__), "configuration.ini")):
            self.configuration.read(os.path.join(os.path.dirname(__file__), "configuration.ini"))
        else:
            self.configuration.read_dict({
                "Database": {
                    "Url": os.environ.get("DATABASE_URL")
                },
                "Discord": {
                    "Token": os.environ.get("DISCORD_TOKEN")
                },
                "Email": {
                    "ApiKey": os.environ.get("EMAIL_API_KEY"),
                    "Addresser": os.environ.get("EMAIL_ADDRESSER")
                }
            })

        self.queries = pugsql.module(os.path.join(os.path.dirname(__file__), "queries"))
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        self.queries.connect(self.configuration.get("Database", "Url"))
        self.queries.create_verification_tokens_table()
        self.queries.create_verified_users_table()

        self.tree.add_command(
            Verify(
                self.configuration.get("Email", "ApiKey"),
                self.configuration.get("Email", "Addresser"),
                self.queries,
            )
        )
        self.tree.add_command(Code(self.queries))

        await self.tree.sync()

    async def on_member_join(self, member: Member) -> None:
        if self.queries.find_by_discord_identifier(member.id):
            await member.add_roles(discord.utils.get(member.guild.roles, name="Verified"))
