import configparser
import logging
import os
import sys

import discord
import pugsql
from discord import ClientException, HTTPException, Member, app_commands

from sentinel.commands.code import Code
from sentinel.commands.unverify import Unverify
from sentinel.commands.verify import Verify


class Sentinel(discord.Client):
    def __init__(self, **options):
        super().__init__(loop=None, intents=discord.Intents().all())
        self.logger = self.create_logging_setup()

        self.configuration = configparser.ConfigParser()

        if os.path.isfile(os.path.join(os.path.dirname(__file__), "configuration.ini")):
            self.configuration.read(os.path.join(os.path.dirname(__file__), "configuration.ini"))
        else:
            self.configuration.read_dict(
                {
                    "Database": {"Url": str(os.environ.get("DATABASE_URL")).replace("postgres://", "postgresql://", 1)},
                    "Discord": {"Token": str(os.environ.get("DISCORD_TOKEN"))},
                    "Email": {
                        "ApiKey": str(os.environ.get("EMAIL_API_KEY")),
                        "Addresser": str(os.environ.get("EMAIL_ADDRESSER")),
                    },
                }
            )

        self.queries = pugsql.module(os.path.join(os.path.dirname(__file__), "queries"))
        self.tree = app_commands.CommandTree(self)

    def create_logging_setup(self):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        return logging.getLogger("Sentinel")

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
        self.tree.add_command(Unverify(self.queries))

        try:
            await self.tree.sync()
        except ClientException:
            self.logger.critical("Failed to sync commands as an invalid or no application token was provided.")
        except HTTPException as exception:
            self.logger.error(f"Failed to sync commands due to an unknown error. Error = {repr(exception.text)}")

    async def on_member_join(self, member: Member) -> None:
        if self.queries.find_by_discord_identifier(member.id):
            await member.add_roles(discord.utils.get(member.guild.roles, name="Verified"))
