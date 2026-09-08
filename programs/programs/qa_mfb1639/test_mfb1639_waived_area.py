"""MFB-1639 row 9 — the ABAWD county waiver, and the county we never send. TEMPORARY.

QA-only, not for production merge.

The ticket's row reads "KS/NC screen with county set (ABAWD county-waiver interaction)". Two
things make it a different test than it looks:

1. **Kansas and North Carolina have no waiver to interact with.** PolicyEngine encodes sub-state
   ABAWD waivers in `gov.usda.snap.work_requirements.abawd.waived_counties.<state>`, and there
   is no `ks.yaml` or `nc.yaml`. Neither state appears in `waived_states` either. So the row as
   written asserts a no-op.

2. **No SNAP variant sends the county.** `is_in_snap_abawd_waived_area` matches on `county_str`,
   which no SNAP calculator declares — every variant sends only its state code. PolicyEngine's
   own documentation for the variable says a household with no county information "falls back to
   the first county alphabetically in its state". So the waiver answer is decided by a county the
   household never supplied, and the screener's `county` field (which we do collect, and which
   `MoCountyDependency` shows we know how to send) is not consulted.

That fallback is not neutral in either direction:

  * Washington's alphabetically-first county, `ADAMS_COUNTY_WA`, *was* on its waived list, so
    every WA household read as waived regardless of where they lived — a false grant.
  * Colorado's is `ADAMS_COUNTY_CO`, which is *not* on Colorado's list (it begins at Alamosa), so
    residents of genuinely waived Colorado counties read as unwaived — a false denial.

Both are currently **dormant**, twice over: every waived-county list has lapsed to `[]`
(MA 2025-07-01, CO 2025-10-01, WA 2026-02-01), and the shipped 40-hour floor satisfies ABAWD via
`is_working` anyway. The tests below pin the mechanism at January 2026, the last month WA's list
was live, so the evidence survives the lists being empty — and confirm the present-day state at
September 2026. FNS approves waivers on a fiscal-year cycle, so the lists will refill.
"""

from datetime import date
from unittest.mock import patch

from programs.programs.cross_white_label.snap.co import CoSnap
from programs.programs.cross_white_label.snap.il import IlSnap
from programs.programs.cross_white_label.snap.ks import KsSnap
from programs.programs.cross_white_label.snap.nc import NcSnap
from programs.programs.cross_white_label.snap.wa import WaSnap
from programs.programs.testing_fixtures.pe_integration import (
    PeIntegrationTestCase,
    add_member,
    make_program,
    make_screen,
)

from programs.programs.qa_mfb1639 import probes
from programs.programs.qa_mfb1639.harness import drop_hours, run_arm
from programs.programs.qa_mfb1639.test_mfb1639_matrix import FRONTIER_VERSION, MAX_ALLOTMENT_ONE

YEAR = "2026"

#: The last month Washington's waived-county list was non-empty (it lapses 2026-02-01), and the
#: last month the CA/IL/NV statewide waivers were in effect (they lapse the same day).
JANUARY = date(2026, 1, 15)

#: Today, for the record: every list has lapsed.
SEPTEMBER = date(2026, 9, 15)

STATES = {
    "ks": (KsSnap, "ks_snap", "KS", "67201", "Sedgwick County"),
    "nc": (NcSnap, "nc_snap", "NC", "27601", "Wake County"),
    "co": (CoSnap, "co_snap", "CO", "80202", "Denver County"),
    "wa": (WaSnap, "wa_snap", "WA", "98101", "King County"),
    "il": (IlSnap, "il_snap", "IL", "60601", "Cook County"),
}


class WaivedAreaTestCase(PeIntegrationTestCase):
    """An unemployed childless adult — the household the work test can actually reach — run in
    the pre-fix arm, where the waiver is the only thing that can save them."""

    pe_version = FRONTIER_VERSION

    def probe_state(self, code: str, screen_id: int, today: date):
        calculator, abbreviation, state_code, zipcode, county = STATES[code]

        screen = make_screen(
            screen_id,
            white_label_code=code,
            state_code=state_code,
            household_size=1,
            zipcode=zipcode,
            county=county,
        )
        adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 30)
        program = make_program(code, abbreviation, YEAR)

        with patch("programs.programs.cross_white_label.snap.base.date") as mock_date:
            mock_date.today.return_value = today
            arm = run_arm(screen, drop_hours(calculator), program)

        # The premise of the whole row: we never told PolicyEngine where they live.
        self.assertNotIn("county_str", arm.payload["household"]["households"]["household"])

        return arm, adult


class TestKansasHasNoWaiverToInteractWith(WaivedAreaTestCase):
    """The ticket's row, as written. No `ks.yaml`, so nothing is waived and the pre-fix payload
    denies — the plain false-$0 case, with no waiver in play."""

    def test_january(self):
        arm, adult = self.probe_state("ks", 1639_90, JANUARY)

        self.assertFalse(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)


class TestNorthCarolinaHasNoWaiverToInteractWith(WaivedAreaTestCase):
    def test_january(self):
        arm, adult = self.probe_state("nc", 1639_91, JANUARY)

        self.assertFalse(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertEqual(arm.value(), 0)


class TestWashingtonWasWaivedOnACountyWeNeverSent(WaivedAreaTestCase):
    """The finding. Washington had a 38-county waiver in January 2026 and we sent no county, so
    PolicyEngine fell back to `ADAMS_COUNTY_WA` — which is on the list. Every WA household read
    as waived, and the ABAWD test passed with zero hours."""

    def test_january_reads_waived_and_survives_the_pre_fix_payload(self):
        arm, adult = self.probe_state("wa", 1639_92, JANUARY)

        self.assertTrue(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_september_is_dormant_because_the_list_lapsed(self):
        """WA's list lapses 2026-02-01, so the same request now reads unwaived and denies. The
        mechanism did not change — only the parameter did."""
        arm, adult = self.probe_state("wa", 1639_93, SEPTEMBER)

        self.assertFalse(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertEqual(arm.value(), 0)


class TestColoradoIsTheOtherDirection(WaivedAreaTestCase):
    """Colorado's fallback county, `ADAMS_COUNTY_CO`, is not on Colorado's waived list, so the
    fallback denies a waiver rather than granting one. Same root cause, opposite sign — and
    invisible in a test that only checks whether the value moved."""

    def test_january_reads_unwaived(self):
        arm, adult = self.probe_state("co", 1639_94, JANUARY)

        self.assertFalse(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertEqual(arm.value(), 0)


class TestIllinoisShowsTheMechanismWorkingCorrectly(WaivedAreaTestCase):
    """Illinois held a *statewide* waiver through 2026-01-31, matched on `state_code`, which we do
    send. So this one is right for the right reason — a useful control on the two above."""

    def test_january_reads_waived_via_the_statewide_list(self):
        arm, adult = self.probe_state("il", 1639_95, JANUARY)

        self.assertTrue(arm.member(probes.IsInSnapAbawdWaivedAreaProbe, adult.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)
