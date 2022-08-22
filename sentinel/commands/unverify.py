import discord
from discord import Member, app_commands
import logging


class Unverify(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="unverify",
            description="Remove your verification status from all Sentinel servers.",
            callback=self.unverify,
        )

        self.logger = logging.getLogger('Sentinel')

        self.queries = queries

    async def unverify_on_mutual_guilds(self, user: Member) -> None:
        for guild in user.mutual_guilds:
            try:
                await user.remove_roles(discord.utils.get(guild.roles, name="Verified"))
            except discord.Forbidden as exception:
                self.logger.warning(f"Failed to remove verified role from user ({str(user.id)}) on guild ({str(guild.id)}). Bot does not have sufficient permissions. Error = {repr(exception)}")
            except discord.HttpException as exception:
                self.logger.error(f"Failed to remove verified role from user ({str(user.id)}) on guild ({str(guild.id)}). An unknown error occurred. Error = {repr(exception)}")

    async def unverify(self, interaction: discord.Interaction) -> None:
        self.queries.delete_verified_user(interaction.user.id)
        self.unverify_on_mutual_guilds(interaction.user)
        await interaction.response.send_message("Your account has been unverified.", ephemeral=True)
