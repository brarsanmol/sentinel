import configparser
import os

import discord


class Sentinel(discord.Client):
    def __init__(self, **options):
        super().__init__(loop=None, **options)

        self.configuration = configparser.ConfigParser()
        self.configuration.read(
            os.path.join(os.path.dirname(__file__), "configuration.ini")
        )

    async def on_ready(self):
        pass
