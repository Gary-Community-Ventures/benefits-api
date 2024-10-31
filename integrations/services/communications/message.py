from typing import Literal
from translations.models import Translation
from screener.models import Message, Screen
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from decouple import config
from django.conf import settings
from twilio.rest import Client
from django.utils import timezone


class MessageUser:
    front_end_domain = config("FRONTEND_DOMAIN")

    cell_account_sid = config("TWILIO_SID")
    cell_auth_token = config("TWILIO_TOKEN")
    cell_from_phone_number = config("TWILIO_PHONE_NUMBER")

    email_from = "myfriendben@codethedream.org"
    email_api_key = config("SENDGRID")

    def __init__(self, screen: Screen, lang: str) -> None:
        self.screen = screen
        self.lang = lang

    def should_send(self) -> bool:
        print("should_send() running.")
        # if settings.DEBUG:
        #     return False

        # if self.screen.is_test_data:
        #     return False

        return True

    def email(self, email: str, send_tests=False):
        print("email() running")
        # if not self.should_send() and not send_tests:
        #     return

        sg = self._email_client()
        from_email = Email(self.email_from)  # Change to your verified sender
        to_email = To(email)  # Change to your recipient
        subject = self._email_subject()
        content = Content("text/html", self._email_body())
        mail = Mail(from_email, to_email, subject, content)

        try:
            print("attempting to send email.")
            sg.client.mail.send.post(request_body=mail.get())
        except Exception as e:
            print("e:", e)

        self.log("emailScreen")

    def _email_client(self):
        return sendgrid.SendGridAPIClient(api_key=self.email_api_key)

    def _email_subject(self):
        return Translation.objects.get(label="sendResults.email-subject").get_lang(self.lang).text

    def _email_body(self):
        words = Translation.objects.get(label="sendResults.email").get_lang(self.lang).text
        url = self._generate_link()

        return words + f' <a href="{url}">{url}</a>'

    def text(self, cell: str, send_tests=False):
        print("text() running.")
        if not self.should_send() and not send_tests:
            print("should not sent is true. returning")
            return

        self._cell_client().messages.create(
            from_=self.cell_from_phone_number,
            body=self._text_body(),
            to=cell,
        )

        self.log("textScreen")

    def _text_body(self):
        words = Translation.objects.get(label="sendResults.email").get_lang(self.lang).text
        url = self._generate_link()

        return f"{words} {url}"

    def _cell_client(self):
        return Client(self.cell_account_sid, self.cell_auth_token)

    def _generate_link(self):
        return f"{self.front_end_domain}/{self.screen.uuid}/results"

    def log(self, type: Literal["emailScreen", "textScreen"]):
        self.screen.last_email_request_date = timezone.now()
        self.screen.save()

        Message.objects.create(
            type=type,
            screen=self.screen,
        )
