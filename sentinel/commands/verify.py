import re
import secrets
import logging
from typing import Any

import discord
import sendgrid
from discord import app_commands
from sendgrid.helpers.mail import Mail
from sqlalchemy.exc import IntegrityError

from sentinel.decorators.is_direct_message_channel import is_direct_message_channel

EMAIL_PATTERN = re.compile(r"[a-zA-Z]+\.[a-zA-Z]+[0-9]{0,2}?@mail\.mcgill\.ca")


class Verify(app_commands.Command):
    def __init__(self, api_key: str, addresser: str, queries: Any):
        super().__init__(
            name="verify",
            description="Send a verification token to your McGill issued e-mail address.",
            callback=self.verify,
        )

        self.logger = logging.getLogger('Sentinel')

        self.mailer = sendgrid.SendGridAPIClient(api_key=api_key)
        self.addresser = addresser

        self.queries = queries

    def generate_token(self):
        return secrets.token_urlsafe(4)

    def get_appropriate_message(self, response):
        match response.status_code:
            case 200:
                self.logger.info("Successfully e-mailed verification token to user.")
                return "A verification code has been sent to your inbox. If you do not see it within a few minutes, please check your spam!"
            case 401:
                self.logger.critical(f"Failed to e-mail verification token. SendGrid failed to authenticate. Error = {repr(response)}")
                return "The bot is currently failing to authenticate with SendGrid."
            case 429:
                self.logger.critical(f"Failed to e-mail verification token. SendGrid rate limit has been reached. Error = {repr(response)}")
                return "The bot is unable to send verification e-mail as it has reached it's SendGrid rate limit."
            case _:
                self.logger.critical(f"Failed to e-mail verification token. Unknown error has occurred. Error = {repr(response)}")
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
        """,
        )

    @app_commands.describe(email_address="Your @mail.mcgill.ca e-mail address.")
    @is_direct_message_channel()
    async def verify(self, interaction: discord.Interaction, email_address: str) -> None:
        if EMAIL_PATTERN.match(email_address, re.IGNORECASE):
            token = self.generate_token()

            try:
                self.logger.info("Saving verification token and e-mail address to database.")
                self.queries.create_verification_token(email_address=email_address, token=token)
            except IntegrityError as exception:
                self.logger.warning(f"Failed to save verification token and e-mail address to table. Error = {repr(exception)}")
                # An exception means we've failed a uniqueness condition.
                await interaction.response.send_message(
                    "The e-mail address provided is already in use.", ephemeral=True
                )
            
            response = self.mailer.send(self.get_message(email_address, token))
            await interaction.response.send_message(self.get_appropriate_message(response), ephemeral=True)
        else:
            self.logger.info("The e-mail address provided does not match the valid REGEX pattern.")
            await interaction.response.send_message("The e-mail address provided is invalid.", ephemeral=True)
