from django.utils.translation import gettext as _
from decouple import config
import sendgrid
import csv
from io import StringIO
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
from screener.views import eligibility_results, eligibility_results_translation
from screener.models import Screen


def email_pdf(target_email, screen_id, language):
    screen = Screen.objects.get(pk=screen_id)

    sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID'))
    from_email = Email("screener@garycommunity.org")  # Change to your verified sender
    to_email = To(target_email)  # Change to your recipient
    domain = config("FRONTEND_DOMAIN")
    url = f"{domain}/results/{screen.uuid}"
    subject = _("Screener Results from My Friend Ben")
    content = Content("text/html",
                      _("Thank you for using MyFriendBen. Click here to review your results.") +
                      f' <a href="{url}">{url}</a>')
    mail = Mail(from_email, to_email, subject, content)

    sg.client.mail.send.post(request_body=mail.get())
