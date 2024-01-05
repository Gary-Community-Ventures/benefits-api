from decouple import config
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from screener.models import Screen
from translations.models import Translation


def email_link(target_email, screen_id, language):
    screen = Screen.objects.get(pk=screen_id)

    sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID'))
    from_email = Email("screener@myfriendben.org")  # Change to your verified sender
    to_email = To(target_email)  # Change to your recipient
    domain = config("FRONTEND_DOMAIN")
    url = f"{domain}/{screen.uuid}/results"
    words = Translation.objects.get(label='sendResults.email').get_lang(language).text
    subject = Translation.objects.get(label='sendResults.email-subject').get_lang(language).text
    content = Content("text/html",
                      words +
                      f' <a href="{url}">{url}</a>')
    mail = Mail(from_email, to_email, subject, content)

    sg.client.mail.send.post(request_body=mail.get())
