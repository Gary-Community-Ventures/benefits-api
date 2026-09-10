from django.db import migrations


#: The FederalPoveryLimit row supplying `Program.year.period`, which is the period every
#: PolicyEngine input and output for this program is requested at.
NEW_YEAR = "2026"
OLD_YEAR = "2025"


def _set_year(apps, from_year, to_year):
    """Move `ma_ccdf` from one period to another, leaving any other period alone.

    Gated on the year it is moving from so the two directions undo each other. An
    unconditional update would have the reverse write 2025 over a row that had been
    moved somewhere else since, or over a null.
    """
    Program = apps.get_model("programs", "Program")
    FederalPoveryLimit = apps.get_model("programs", "FederalPoveryLimit")

    try:
        fpl = FederalPoveryLimit.objects.get(year=to_year, period=to_year)
    except FederalPoveryLimit.DoesNotExist:
        # Nothing to point at. Better to leave the program on its current period than to
        # null out the year, which raises on every screen the program is calculated for.
        # Loud, because the program is left on the limit this migration exists to escape.
        print(f"ma_ccdf: no FederalPoveryLimit for {to_year}; leaving the program on {from_year}")
        return

    Program.objects.filter(name_abbreviated="ma_ccdf", year__year=from_year).update(year=fpl)


def set_ma_ccdf_year_2026(apps, schema_editor):
    """
    Move `ma_ccdf` to the 2026 period.

    Massachusetts CCFA reads one of two income limits: 85% of state median income for a
    household already enrolled, and a new-applicant limit that PolicyEngine holds at 50%
    before 2026-01-01 and 85% from it. Screening asks the new-applicant question, so at the
    2025 period the program applies the 50% limit -- measured, that moves a two-person
    household's ceiling from $91,139 to $53,611.

    The federal CCDF variables this program used to read had a single 85% limit at any
    period, so the 2025 period cost nothing while they were in use and costs a large share
    of eligible Massachusetts families now. There is no config file for this program --
    `year` is set through the admin -- so the bump ships here rather than as an import that
    could lag the deploy.
    """
    _set_year(apps, OLD_YEAR, NEW_YEAR)


def revert_ma_ccdf_year(apps, schema_editor):
    _set_year(apps, NEW_YEAR, OLD_YEAR)


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0175_ks_lieap_on_has_benefits_step"),
    ]
    operations = [
        migrations.RunPython(set_ma_ccdf_year_2026, revert_ma_ccdf_year),
    ]
