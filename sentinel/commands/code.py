import discord
from discord import User, app_commands
from discord.errors import HttpException, Forbidden

from sentinel.decorators.is_direct_message_channel import is_direct_message_channel


class Code(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="code",
            description="Verify your identity with the token e-mailed to you.",
            callback=self.code,
        )

        self.logger = logging.getLogger('Sentinel')

        self.queries = queries

    async def verify_on_mutual_guilds(self, user: User) -> None:
        for guild in user.mutual_guilds:
            try:
                await user.add_roles(discord.utils.get(guild.roles, name="Verified"))
                self.logger.info(f"Successfully added verified role to user ({str(user.id)}) on guild ({str(guild.id)}).")
            except Forbidden as exception:
                self.logger.warning(f"Failed to add verified role to user ({str(user.id)}) on guild ({str(guild.id)}). Bot does not have sufficient permissions in guild. Error = {repr(exception)}")
            except HttpException as exception:
                self.logger.error(f"Failed to add verified role to user ({str(user.id)}) on guild ({str(guild.id)}). An unknown error occurred. Error = {repr(exception)}")

    @app_commands.describe(token="The verification token e-mailed to you.")
    @is_direct_message_channel()
    async def code(self, interaction: discord.Interaction, token: str) -> None:
        if self.queries.delete_verification_token(token=token) > 0:
            self.queries.create_verified_user(identifier=interaction.user.id)
            await self.verify_on_mutual_guilds(interaction.user)
            interaction.response.send_message("You have been successfully verified!", ephemeral=True)
        else:
            interaction.response.send_message("The verification token provided is invalid.", ephemeral=True)
