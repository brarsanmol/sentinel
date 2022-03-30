import re

import discord
from discord import app_commands

EMAIL_PATTERN = re.compile(r"[a-zA-Z]+\.[a-zA-Z]+@mail\.mcgill\.ca")


def is_direct_message_channel():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.channel.type == discord.ChannelType.private

    return app_commands.check(predicate)


class Verify(app_commands.Command):
    def __init__(self):
        super().__init__(name="verify", description="", callback=self.verify)

    @app_commands.describe(email_address="Your @mail.mcgill.ca e-mail address.")  # noqa
    @is_direct_message_channel()
    async def verify(
        self, interaction: discord.Interaction, email_address: str
    ) -> None:
        if EMAIL_PATTERN.match(email_address, re.IGNORECASE):
            await interaction.response.send_message(
                "The e-mail address provided is valid.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "The e-mail address provided is invalid.", ephemeral=True
            )
