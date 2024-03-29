import logging

import discord
from discord import Forbidden, HTTPException, Member, User, app_commands

from sentinel.decorators.is_direct_message_channel import is_direct_message_channel


class Code(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="code",
            description="Verify your identity with the token e-mailed to you.",
            callback=self.code,
        )

        self.logger = logging.getLogger("Sentinel")

        self.queries = queries

    async def verify_on_mutual_guilds(self, user: User) -> None:
        for guild in user.mutual_guilds:
            try:
                await guild.get_member(user.id).add_roles(discord.utils.get(guild.roles, name="Verified"))
                self.logger.info(
                    f"Successfully added verified role to user ({str(user.id)}) on guild ({str(guild.id)})."
                )
            except Forbidden as exception:
                self.logger.warning(
                    f"Failed to add verified role to user ({str(user.id)}) on guild ({str(guild.id)}). Bot does not have sufficient permissions in guild. Error = {repr(exception)}"
                )
            except HTTPException as exception:
                self.logger.error(
                    f"Failed to add verified role to user ({str(user.id)}) on guild ({str(guild.id)}). An unknown error occurred. Error = {repr(exception)}"
                )

    @app_commands.describe(token="The verification token e-mailed to you.")
    @is_direct_message_channel()
    async def code(self, interaction: discord.Interaction, token: str) -> None:
        result = self.queries.find_by_verification_token(token=token)
        if self.queries.delete_verification_token(token=token) > 0:
            self.queries.create_verified_user(identifier=interaction.user.id, email_address=result["email_address"])
            await self.verify_on_mutual_guilds(interaction.user)
            await interaction.response.send_message("You have been successfully verified!", ephemeral=True)
        else:
            await interaction.response.send_message("The verification token provided is invalid.", ephemeral=True)
