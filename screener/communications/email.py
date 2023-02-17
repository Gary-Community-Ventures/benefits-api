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
    raw_data = eligibility_results(screen)
    data = eligibility_results_translation(raw_data, language)

    data_reduced = []
    for item in data:
        item.pop('legal_status_required', None)
        item.pop('failed_tests', None)
        item.pop('passed_tests', None)
        item.pop('short_name', None)
        item.pop('apply_button_link', None)
        if item['eligible']:
            item.pop('eligible', None)
            data_reduced.append(item)
    data_reduced = sorted(data_reduced, key=lambda x: x['estimated_value'], reverse=True)
    col_names = list(data_reduced[0].keys())
    cell_text = []
    cell_text.append(col_names)
    for item in data_reduced:
        cell_text.append(list(item.values()))

    f = StringIO()
    csv.writer(f).writerows(cell_text)
    encoded = base64.b64encode(f.getvalue().encode())
    encoded = str(encoded, 'utf-8')
    sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID'))
    from_email = Email("screener@garycommunity.org")  # Change to your verified sender
    to_email = To(target_email)  # Change to your recipient
    domain = config("FRONTEND_DOMAIN")
    url = f"{domain}/results/{screen.uuid}"
    subject = _("Screener Results from My Friend Ben")
    content = Content("text/html",
                      _("Thank you for using MyFriendBen. Click here to review your results.") +
                      f'<a href="{url}">{url}</a>')
    mail = Mail(from_email, to_email, subject, content)
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('text/csv')
    attachment.file_name = FileName('results.csv')
    attachment.disposition = Disposition('attachment')
    mail.add_attachment(attachment)

    sg.client.mail.send.post(request_body=mail.get())
