import re
import secrets

import discord
import sendgrid
from discord import app_commands
from sendgrid.helpers.mail import Mail

from sentinel.decorators.is_direct_message_channel import (  # noqa
    is_direct_message_channel,
)

EMAIL_PATTERN = re.compile(r"[a-zA-Z]+\.[a-zA-Z]+@mail\.mcgill\.ca")


class Verify(app_commands.Command):
    def __init__(self, api_key: str, addresser: str):
        super().__init__(name="verify", description="", callback=self.verify)
        self.mailer = sendgrid.SendGridAPIClient(api_key=api_key)
        self.addresser = addresser

    def generate_token(self):
        return secrets.token_urlsafe(4)

    def get_message(self, addressee: str, token: str) -> None:
        return Mail(
            from_email=self.addresser,
            to_emails=addressee,
            subject="Discord Verification Code",
            plain_text_content=f"""
        Hi there,

        Your Sentinel discord verification code is {token}.

        To verify yourself enter /code {token} in your direct message channel with Sentinel.
        """,  # noqa
        )

    @app_commands.describe(email_address="Your @mail.mcgill.ca e-mail address.")  # noqa
    @is_direct_message_channel()
    async def verify(
        self, interaction: discord.Interaction, email_address: str
    ) -> None:
        if EMAIL_PATTERN.match(email_address, re.IGNORECASE):
            response = self.mailer.send(
                self.get_message(email_address, self.generate_token())
            )

            match response.status_code:
                case 200:
                    await interaction.response.send_message("", ephemeral=True)
                case 401:
                    await interaction.response.send_message("", ephemeral=True)
                case 429:
                    await interaction.response.send_message("", ephemeral=True)
                case _:
                    await interaction.response.send_message("", ephemeral=True)
        else:
            await interaction.response.send_message(
                "The e-mail address provided is invalid.", ephemeral=True
            )
