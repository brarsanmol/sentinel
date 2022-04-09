import discord
from discord import Member, app_commands


class Unverify(app_commands.Command):
    def __init__(self, queries):
        super().__init__(
            name="unverify",
            description="Remove your verification status from all Sentinel servers.",
            callback=self.unverify,
        )

        self.queries = queries

    async def unverify_on_mutual_guilds(self, user: Member) -> None:
        for guild in user.mutual_guilds:
            await user.remove_roles(discord.utils.get(guild.roles, name="Verified"))

    async def unverify(self, interaction: discord.Interaction) -> None:
        self.queries.delete_verified_user(interaction.user.id)
        self.unverify_on_mutual_guilds(interaction.user)
        interaction.response.send_message("Your account has been unverified.", ephemeral=True)
