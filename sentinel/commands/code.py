import discord
from discord import app_commands

from sentinel.decorators.is_direct_message_channel import is_direct_message_channel


class Code(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="code",
            description="Verify your identity with the token e-mailed to you.",
            callback=self.code,
        )

        self.queries = queries

    @app_commands.describe(token="The verification token e-mailed to you.")
    @is_direct_message_channel()
    async def code(self, interaction: discord.Interaction, token: str) -> None:
        if self.queries.delete_token(token=token) > 0:
            interaction.response.send_message("You have been successfully verified!", ephemeral=True)
        else:
            interaction.response.send_message("The verification token provided is invalid.", ephemeral=True)
