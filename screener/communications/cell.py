from decouple import config
from twilio.rest import Client


def text_link(cell, screen, language):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = config("TWILIO_SID")
    auth_token = config("TWILIO_TOKEN")
    from_phone_number = config("TWILIO_PHONE_NUMBER")
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=from_phone_number,
        body=f"Here is a link to your results: https://screener.myfriendben.org/results/{screen.uuid}",
        to="+1"+str(cell),
    )

    print(message.body)
