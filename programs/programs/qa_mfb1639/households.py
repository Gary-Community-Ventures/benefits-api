"""MFB-1639 QA households — TEMPORARY, not for production merge.

The ticket's scenario matrix, as households. Three of its nine rows do not probe what they
were written to probe, because PolicyEngine's SNAP work rules moved after the ticket was
filed; those are kept and re-pointed at the boundary that actually decides the result, and the
divergence is recorded in PE_FRONTIER_MATRIX_2026-09-08.md rather than silently dropped.

What actually decides a SNAP work-test outcome on the pinned model:

  * `meets_snap_general_work_requirements` returns `exempted | compliant`, and `compliant`
    defaults True (`is_snap_work_registration_noncompliant` defaults False). PolicyEngine made
    that change on 2026-07-08, *before* 1.815.1. So the general 30-hour test cannot deny.
  * `meets_snap_work_requirements_person` therefore governs via ABAWD alone — and only when no
    household member is under the dependent-child threshold, which HR1 moved to **14**. Any
    household with a member under 14 is routed around ABAWD entirely.
  * ABAWD needs >= 20 weekly hours or an exemption. Its exempt age is **65** post-HR1
    (2025-07-04), not the 55 it was, and not the 60 that exempts from the general test.

So every row meant to test hours has to be childless (or have no member under 14), and the
"60+" row has to straddle 65 rather than 60.

Incomes are kept well inside every state's SNAP gross-income limit so the work test is the only
lever — a row that failed on income would prove nothing about hours.
"""

from programs.programs.testing_fixtures.pe_integration import (
    add_income,
    add_member,
    make_program,
    make_screen,
)

YEAR = "2026"

#: Kansas is a clean federal passthrough (`KsSnap` adds only the state code), so it carries the
#: rows that are about federal work rules rather than about a state's elections.
KS = {"white_label_code": "ks", "state_code": "KS", "zipcode": "67201", "county": "Sedgwick County"}


def _screen(screen_id: int, household_size: int, **where):
    return make_screen(screen_id, household_size=household_size, **where)


def hourly_worker(screen_id: int = 1639_01):
    """Row 1 — working single adult, hours *reported* on an hourly stream.

    $20/hr for 15 hours a week. 15 is deliberately under ABAWD's 20-hour threshold: it is the
    only way this row can distinguish the 40-hour floor from the hours the screen evidences,
    which is the MFB-1637 policy decision (MFB-1731 owns the revisit).
    """
    screen = _screen(screen_id, 1, **KS)
    adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 30)
    add_income(adult, amount=20, income_type="wages", frequency="hourly")
    adult.income_streams.update(hours_worked=15)
    return screen, make_program("ks", "ks_snap", YEAR), adult


def salaried_worker(screen_id: int = 1639_02):
    """Row 2 — working single adult, salaried, so hours are approximated rather than reported.

    $1,200/mo at the $7.25 federal floor over 4 weeks = 41.4 weekly hours, which clears both
    thresholds on its own. Nothing is reported, so the control arm sends nothing at all.
    """
    screen = _screen(screen_id, 1, **KS)
    adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 30)
    add_income(adult, amount=1_200, income_type="wages", frequency="monthly")
    return screen, make_program("ks", "ks_snap", YEAR), adult


def unemployed_abawd(screen_id: int = 1639_03):
    """Row 3 — unemployed childless adult. The row the hours policy actually rests on.

    No income of any kind, so `reported_hours()` is 0 and the 40-hour floor is the only thing
    asserting a work test is met. This is the household MFB-1637 decided to hold harmless on no
    evidence of work, and the one a "real hours" policy would deny.
    """
    screen = _screen(screen_id, 1, **KS)
    adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 30)
    return screen, make_program("ks", "ks_snap", YEAR), adult


def family_with_child(age: int, screen_id: int):
    """Rows 4 and 5 — a working parent and one child of the given age.

    The ticket splits these on 6 ("parent exempt via child under 6"). On the pinned model the
    boundary that matters is **14**: under it, `meets_snap_work_requirements_person` skips ABAWD
    for every member of the household, and the general test cannot deny. A child of 8 — the
    ticket's "youngest child 6+" case — is therefore just as protected as a child of 3, and only
    a household whose youngest is 14 or over is exposed at all.
    """
    screen = _screen(screen_id, 2, **KS)
    parent = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 40)
    child = add_member(screen, screen_id * 10 + 2, "child", age)
    return screen, make_program("ks", "ks_snap", YEAR), parent, child


def disabled_adult(screen_id: int = 1639_06):
    """Row 6 — disabled childless adult. `is_disabled` exempts from ABAWD outright."""
    screen = _screen(screen_id, 1, **KS)
    adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 40, disabled=True)
    return screen, make_program("ks", "ks_snap", YEAR), adult


def older_adult(age: int, screen_id: int):
    """Row 7 — the ticket's "60+ adult", straddling the age that actually exempts.

    The general test exempts at 60, but it cannot deny anyway. ABAWD's exempt age is 65 post-HR1,
    so 62 is exposed and 66 is not. No income, so age is the only lever.
    """
    screen = _screen(screen_id, 1, **KS)
    adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", age)
    return screen, make_program("ks", "ks_snap", YEAR), adult
