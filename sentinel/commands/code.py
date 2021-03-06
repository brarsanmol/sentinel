import discord
from discord import User, app_commands

from sentinel.decorators.is_direct_message_channel import is_direct_message_channel


class Code(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="code",
            description="Verify your identity with the token e-mailed to you.",
            callback=self.code,
        )

        self.queries = queries

    async def verify_on_mutual_guilds(self, user: User) -> None:
        for guild in user.mutual_guilds:
            await user.add_roles(discord.utils.get(guild.roles, name="Verified"))

    @app_commands.describe(token="The verification token e-mailed to you.")
    @is_direct_message_channel()
    async def code(self, interaction: discord.Interaction, token: str) -> None:
        if self.queries.delete_verification_token(token=token) > 0:
            self.queries.create_verified_user(identifier=interaction.user.id)
            await self.verify_on_mutual_guilds(interaction.user)
            interaction.response.send_message("You have been successfully verified!", ephemeral=True)
        else:
            interaction.response.send_message("The verification token provided is invalid.", ephemeral=True)
