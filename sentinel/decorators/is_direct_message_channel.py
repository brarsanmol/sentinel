import discord
from discord import app_commands


def is_direct_message_channel():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.channel.type == discord.ChannelType.private

    return app_commands.check(predicate)
