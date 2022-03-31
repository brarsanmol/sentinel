import re
import secrets
from typing import Any

import discord
import sendgrid
from discord import app_commands
from sendgrid.helpers.mail import Mail

from sentinel.decorators.is_direct_message_channel import (  # noqa
    is_direct_message_channel,
)

EMAIL_PATTERN = re.compile(r"[a-zA-Z]+\.[a-zA-Z]+@mail\.mcgill\.ca")


class Verify(app_commands.Command):
    def __init__(self, api_key: str, addresser: str, queries: Any):
        super().__init__(name="verify", description="", callback=self.verify)

        self.mailer = sendgrid.SendGridAPIClient(api_key=api_key)
        self.addresser = addresser

        self.queries = queries

    def generate_token(self):
        return secrets.token_urlsafe(4)

    def get_appropriate_message(self, status_code: int):
        match status_code:
            case 200:
                return "A verification code has been sent to your inbox."
            case 401:
                return "The bot is currently failing to authenticate with SendGrid."
            case 429:
                return "The bot is unable to send verification e-mail as it has reached it's SendGrid rate limit."
            case _:
                return "An unknown error occurred."

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
    async def verify(self, interaction: discord.Interaction, email_address: str) -> None:
        if EMAIL_PATTERN.match(email_address, re.IGNORECASE):
            token = self.generate_token()

            # TODO - SQL throw's an exception when a non-unique value is submitted, catch this for every driver.
            try:
                self.queries.create_token(email_address=email_address, token=token)
            except:  # noqa
                await interaction.response.send_message(
                    "The e-mail address provided is already in use.", ephemeral=True
                )

            response = self.mailer.send(self.get_message(email_address, token))
            await interaction.response.send_message(self.get_appropriate_message(response.status_code), ephemeral=True)
        else:
            await interaction.response.send_message("The e-mail address provided is invalid.", ephemeral=True)
