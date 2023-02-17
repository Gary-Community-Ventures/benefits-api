from django.utils.translation import gettext as _
from decouple import config
from twilio.rest import Client


def text_link(cell, screen, language):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = config("TWILIO_SID")
    auth_token = config("TWILIO_TOKEN")
    from_phone_number = config("TWILIO_PHONE_NUMBER")
    client = Client(account_sid, auth_token)
    domain = config("FRONTEND_DOMAIN")
    words = _("Here is a link to your results")
    url = f"{domain}/results/{screen.uuid}"
    message = client.messages.create(
        from_=from_phone_number,
        body=f"{words}: {url}",
        to="+1"+str(cell),
    )

    print(message.body)
