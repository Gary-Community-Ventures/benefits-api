from django.contrib import admin
from django.db.models.signals import post_save
from django.utils.translation import override
from screener.email import email_pdf
from .models import Message, Screen, EligibilitySnapshot
from django.dispatch import receiver
from .models import IncomeStream

admin.site.register(Screen)
admin.site.register(Message)
admin.site.register(IncomeStream)


@receiver(post_save, sender=Message)
def send_screener_email(sender, instance, created, **kwargs):
    if created and instance.type == 'emailScreen':
        if instance.email and instance.screen:
            language = 'en-us'
            if instance.screen.request_language_code:
                language = instance.screen.request_language_code

            with override(language):
                email_pdf(instance.email, instance.screen.id, language)


def generate_bwf_snapshots():
    bwf_ids = ['123', '121001', '119201', '119151', '118901', '119001', '118751', '118301', '118001', '117651',
               '117501', '117451', '116601', '116551', '116351', '116151', '115851', '115801', '114751', '114501',
               '114401', '114201', '114001', '113901', '113651', '113501', '113451', '111301', '108751', '108151',
               '107101', '106551', '106201', '101901', '101701', '100451', '100201', '95051', '93801', '82751',
               '82701', '77151', '71851', '71051', '70851', '70751', '70701', '70351', '70301', '70201', '68651',
               '67401', '67001', '66651', '66601', '66301', '65851', '65101', '65001', '64951', '64801', '64751',
               '62951', '59051', '59001', '58801', '58201', '57851', '57651', '57601', '56801', '56351', '56101',
               '55901', '55801', '55501', '55451', '55051', '54951', '54801', '54751', '54551', '76501', '54151',
               '53351', '53051', '52701', '52351', '52301', '52151', '51601', '51151', '51001', '49901', '49851',
               '49551', '49251', '48901', '48701', '48551', '48501', '48401', '47751', '46951', '46751', '46151',
               '46001', '41201', '40701', '40101']
    screens = Screen.objects.filter(external_id__in=bwf_ids).order_by('-submission_date')
    total_screens = screens.count()
    print("Total BWF Screens found: " + str(total_screens))

    screens_without_snapshots = []
    screen_eids = []
    for screen in screens:
        existing_snapshots = EligibilitySnapshot.objects.filter(screen=screen)
        if len(existing_snapshots) <= 0 and screen.external_id not in screen_eids:
            screens_without_snapshots.append(screen)
            screen_eids.append(screen.external_id)

    total_screens_without_snapshots = len(screens_without_snapshots)
    print("Total BWF screens without snapshots found: " + str(total_screens_without_snapshots))
    count = 0
    for screen in screens_without_snapshots:
        eligibility_snapshot = EligibilitySnapshot(screen=screen)
        eligibility_snapshot.save()
        eligibility_snapshot.generate_program_snapshots()
        count += 1
        print("Snapshot " + str(count) + "/" + str(total_screens_without_snapshots) + " generated for " + str(screen.external_id))


def generate_nav_snapshots():
    nav_ids = ['3171', '3183', '3200', '3230', '3233', '3243', '3245', '3248', '3260', '3373', '3374', '3375', '3376',
               '3377', '3300', '3301', '3310', '3312', '3313', '3316', '3343', '3363', '3364', '3365', '3368', '3397',
               '3398', '3399', '2686', '2693', '2690', '2688', '2694', '2707', '2715', '2710', '2711', '2709', '2713']
    screens = Screen.objects.filter(id__in=nav_ids)
    total_screens = screens.count()

    count = 0
    for screen in screens:
        eligibility_snapshot = EligibilitySnapshot(screen=screen)
        eligibility_snapshot.save()
        eligibility_snapshot.generate_program_snapshots()
        count += 1
        print("Snapshot " + str(count) + "/" + str(total_screens) + " generated for " + str(screen.id))


def generate_bia_sample_snapshot():
    nav_ids = ['4097', '4147', '4148']
    screens = Screen.objects.filter(id__in=nav_ids)
    total_screens = screens.count()

    count = 0
    for screen in screens:
        eligibility_snapshot = EligibilitySnapshot(screen=screen)
        eligibility_snapshot.save()
        eligibility_snapshot.generate_program_snapshots()
        count += 1
        print("Snapshot " + str(count) + "/" + str(total_screens) + " generated for " + str(screen.id))
