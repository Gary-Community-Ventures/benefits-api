"""MFB-1639 — the ticket's scenario matrix, run against PolicyEngine's frontier. TEMPORARY.

QA-only, not for production merge.

Each test is one (scenario, arm) pair and makes exactly one POST to household.api, which is what
lets a cassette hold a single meaningful interaction — `conftest.policy_engine_body` raises on a
body mismatch rather than returning False, so a cassette holding two PolicyEngine interactions
cannot be replayed reliably. Every arm therefore asserts its own absolute value; a re-record at a
newer version surfaces a change instead of passing on "still differs". The arm-to-arm comparison
is drawn in PE_FRONTIER_MATRIX_2026-09-08.md.

The three arms (see `harness`):

  shipped     `pe_inputs` as on origin/main — hours sent, floored at 40 for members 16+.
  control     hours dropped entirely: the pre-MFB-1637 payload, and so the failure mode the
              ticket predicts ("expect false $0 SNAP results per the audit").
  floorless   hours sent without the floor: what the "real/approximated hours" option in
              MFB-1637's policy decision would have produced. Differs from shipped only where
              reported hours fall under 40. MFB-1731 owns the revisit.

Read the whole matrix and the three stale premises it exposes in
PE_FRONTIER_MATRIX_2026-09-08.md.
"""

from datetime import date
from unittest.mock import patch

from programs.programs.cross_white_label.snap.ks import KsSnap
from programs.programs.testing_fixtures.pe_integration import PeIntegrationTestCase

from programs.programs.qa_mfb1639 import households, probes
from programs.programs.qa_mfb1639.harness import drop_hours, reported_hours_only, run_arm

#: What `frontier` resolved to when these cassettes were recorded (`GET /versions/us` on
#: 2026-09-08; `current` was 1.821.2 the same day). Pinned as an exact version because
#: `PolicyEngineConfig.clean` rejects the floating aliases — and because a pin is the only thing
#: that keeps this evidence reproducible after frontier moves again. Every `min_pe_version` floor
#: in `pe_dependencies/` is <= (1, 779, 3), so gating here sends the identical input set the
#: `frontier` alias itself would have.
FRONTIER_VERSION = "1.821.10"

#: `Snap.pe_period_month` reads today's month, which travels in the request body, so the date is
#: pinned rather than taken from the wall clock. January, matching MFB-1640's evidence and
#: `test_mo_integration`: the maximum allotment steps up each October, so a wall-clock month
#: would move every asserted dollar figure. The arms differ only by the hours input, so the
#: work-test verdicts this ticket is about do not depend on which month is asked about.
TODAY = date(2026, 1, 15)

#: FY2026 maximum allotments, the figures the zero-income rows land on.
MAX_ALLOTMENT_ONE = 298
MAX_ALLOTMENT_TWO = 546


class Mfb1639MatrixTestCase(PeIntegrationTestCase):
    pe_version = FRONTIER_VERSION

    def arm(self, screen, program, calculator_class):
        """One arm, with the date pinned across both request assembly and response reads.

        The patch has to span the read as well: `Arm` snapshots its periods inside this block
        because `pe_period_month` would otherwise resolve the wall-clock month when the response
        is read, and ask PolicyEngine's answer for a month the request never named.
        """
        with patch("programs.programs.cross_white_label.snap.base.date") as mock_date:
            mock_date.today.return_value = TODAY
            return run_arm(screen, calculator_class, program)


class TestRow1HourlyWorker(Mfb1639MatrixTestCase):
    """Row 1 — working single adult, hours *reported* on an hourly stream (15 hrs/wk).

    The only row where all three arms differ, and so the row that prices MFB-1637's policy
    choice: 15 reported hours is under ABAWD's 20-hour threshold, so the 40-hour floor is what
    holds this household eligible.
    """

    def test_shipped(self):
        screen, program, adult = households.hourly_worker()

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(adult.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertTrue(arm.eligibility.eligible)
        self.assertEqual(arm.value(), 47 * 12)

    def test_control(self):
        """Pre-MFB-1637: nothing sent, so the reported 15 hours never reach PolicyEngine."""
        screen, program, adult = households.hourly_worker()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertIsNone(arm.hours_sent(adult.id))
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertFalse(arm.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(arm.value(), 0)

    def test_floorless(self):
        """The cost of the floor, priced: sending the 15 hours this screen actually evidences
        denies the household, because ABAWD wants 20. Same $0 as sending nothing at all."""
        screen, program, adult = households.hourly_worker()

        arm = self.arm(screen, program, reported_hours_only(KsSnap))

        self.assertEqual(arm.hours_sent(adult.id), 15)
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)


class TestRow2SalariedWorker(Mfb1639MatrixTestCase):
    """Row 2 — working single adult, salaried, so hours are approximated instead of reported.

    $1,200/mo at the $7.25 federal floor over 4 weeks = 41.38 weekly hours, which clears both
    thresholds on the approximation alone. The floor is inert here — shipped and floorless agree.
    """

    def test_shipped(self):
        screen, program, adult = households.salaried_worker()

        arm = self.arm(screen, program, KsSnap)

        self.assertAlmostEqual(arm.hours_sent(adult.id), 1200 / 7.25 / 4)
        self.assertTrue(arm.eligibility.eligible)
        self.assertEqual(arm.value(), 72 * 12)

    def test_control(self):
        screen, program, adult = households.salaried_worker()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertIsNone(arm.hours_sent(adult.id))
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)

    def test_floorless_matches_shipped(self):
        """The approximation is already above 40, so removing the floor changes nothing."""
        screen, program, adult = households.salaried_worker()

        arm = self.arm(screen, program, reported_hours_only(KsSnap))

        self.assertAlmostEqual(arm.hours_sent(adult.id), 1200 / 7.25 / 4)
        self.assertEqual(arm.value(), 72 * 12)


class TestRow3UnemployedAbawd(Mfb1639MatrixTestCase):
    """Row 3 — unemployed childless adult (ABAWD).

    The row the MFB-1637 policy decision rests on: no earned income, so the 40-hour floor is the
    only thing asserting a work test is met, on a household that reported no work at all.
    """

    def test_shipped(self):
        screen, program, adult = households.unemployed_abawd()

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(adult.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertTrue(arm.spm(probes.IsSnapEligibleProbe))
        self.assertTrue(arm.eligibility.eligible)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_control(self):
        """Pre-MFB-1637: no hours sent, so PolicyEngine reads 0 and ABAWD denies the unit."""
        screen, program, adult = households.unemployed_abawd()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertIsNone(arm.hours_sent(adult.id))
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertFalse(arm.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(arm.value(), 0)

    def test_floorless(self):
        """A real-hours policy would deny this household too: nothing reported is zero hours."""
        screen, program, adult = households.unemployed_abawd()

        arm = self.arm(screen, program, reported_hours_only(KsSnap))

        self.assertEqual(arm.hours_sent(adult.id), 0)
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)

    def test_the_general_test_cannot_deny_even_with_no_hours(self):
        """PolicyEngine's 2026-07-08 change, which this ticket predates: the general 30-hour test
        returns `exempted | compliant`, and `compliant` defaults True. So the $0 above is ABAWD's
        doing alone — which is why every hours row in this matrix has to be childless."""
        screen, program, adult = households.unemployed_abawd()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertTrue(arm.member(probes.MeetsSnapGeneralWorkRequirementsProbe, adult.id))
        self.assertFalse(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, adult.id))


class TestRow4YoungestChildSchoolAge(Mfb1639MatrixTestCase):
    """Row 4 — "family whose youngest child is 6+ (parent not exempt via child-under-6)".

    The ticket's premise is stale, and this row is kept to show why. Post-HR1 the household
    dependent-child threshold is **14**, and `meets_snap_work_requirements_person` routes every
    member of a household containing someone under it around ABAWD entirely. With the general
    test unable to deny, a parent whose youngest is 8 is exempt whatever we send.
    """

    def test_control_does_not_move_with_a_child_of_eight(self):
        screen, program, parent, child = households.family_with_child(8, 1639_04)

        arm = self.arm(screen, program, drop_hours(KsSnap))

        # ABAWD fails on the parent, and it does not matter: the person-level gate skipped it.
        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, parent.id))
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_TWO * 12)

    def test_shipped_agrees_with_a_child_of_eight(self):
        screen, program, parent, child = households.family_with_child(8, 1639_04)

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(parent.id), 40)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_TWO * 12)


class TestRow4YoungestChildFourteenPlus(Mfb1639MatrixTestCase):
    """Row 4, re-pointed at the boundary that actually decides it: youngest child 15.

    This is where the ticket's row becomes probative — and it exposes a failure mode the ticket
    does not describe. The household is **not** denied outright. PolicyEngine removes the
    noncompliant adult from the SNAP unit rather than zeroing the unit, so the allotment silently
    drops from the two-person figure to the one-person figure. A QA check comparing $0 against
    nonzero would have called this a pass.
    """

    def test_shipped(self):
        screen, program, parent, child = households.family_with_child(15, 1639_44)

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(parent.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_TWO * 12)

    def test_control_silently_halves_the_allotment(self):
        screen, program, parent, child = households.family_with_child(15, 1639_44)

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertFalse(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, child.id))
        # Still "eligible", at the one-person allotment: the parent is out of the unit.
        self.assertTrue(arm.spm(probes.IsSnapEligibleProbe))
        self.assertTrue(arm.eligibility.eligible)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_floorless_halves_it_too(self):
        """Zero reported hours is zero either way — the floor is what holds the unit together."""
        screen, program, parent, child = households.family_with_child(15, 1639_44)

        arm = self.arm(screen, program, reported_hours_only(KsSnap))

        self.assertEqual(arm.hours_sent(parent.id), 0)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)


class TestRow5ChildUnderSix(Mfb1639MatrixTestCase):
    """Row 5 — family with a child under 6 (parent exempt). Doubly protected: the under-14
    household gate skips ABAWD, and caring for a child under 6 is itself an ABAWD exemption."""

    def test_control_does_not_move(self):
        screen, program, parent, child = households.family_with_child(3, 1639_05)

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, parent.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_TWO * 12)

    def test_shipped_agrees(self):
        screen, program, parent, child = households.family_with_child(3, 1639_05)

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.value(), MAX_ALLOTMENT_TWO * 12)


class TestRow6DisabledAdult(Mfb1639MatrixTestCase):
    """Row 6 — disabled childless adult. `is_disabled` exempts from ABAWD outright, so the floor
    is inert and the pre-fix payload was never at risk here."""

    def test_control_does_not_move(self):
        screen, program, adult = households.disabled_adult()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertIsNone(arm.hours_sent(adult.id))
        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_shipped_agrees(self):
        screen, program, adult = households.disabled_adult()

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(adult.id), 40)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)


class TestRow7OlderAdultBelowSixtyFive(Mfb1639MatrixTestCase):
    """Row 7 — the ticket's "60+ adult", at 62.

    The ticket assumed 60 exempts. It exempts from the *general* test, which cannot deny anyway;
    ABAWD's exempt age is 65 post-HR1 (2025-07-04, having moved 50 -> 51 -> 53 -> 55 -> 65). A
    62-year-old is fully exposed, which is what MFB-1637's own live check saw in its 62-year-old
    case.
    """

    def test_control_denies(self):
        screen, program, adult = households.older_adult(62, 1639_07)

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)

    def test_shipped_holds_them_eligible(self):
        screen, program, adult = households.older_adult(62, 1639_07)

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(adult.id), 40)
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)


class TestRow7OlderAdultAtSixtySix(Mfb1639MatrixTestCase):
    """Row 7's other side — 66, past the post-HR1 ABAWD exempt age, so genuinely inert."""

    def test_control_does_not_move(self):
        screen, program, adult = households.older_adult(66, 1639_77)

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_shipped_agrees(self):
        screen, program, adult = households.older_adult(66, 1639_77)

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)


class TestOneFailingAdultDoesNotZeroTheHousehold(Mfb1639MatrixTestCase):
    """MFB-1637 states the impact as "one failing adult can zero out the household's SNAP". The
    matrix in this ticket has no two-adult row, so that claim was never run. It is too strong.

    Two childless adults, one earning and one reporting nothing, read in the floorless arm — the
    only arm that can put one passing and one failing adult in the same unit. The failing adult is
    removed from the SNAP unit and the household keeps the one-person allotment. Same mechanism as
    the parent-and-teenager case in `TestRow4YoungestChildFourteenPlus`: a partial loss, not a
    denial.

    The distinction matters for monitoring. A household that loses one of two adults is still
    "eligible" with a plausible number, so nothing about the result looks wrong.
    """

    def test_floorless_removes_only_the_adult_without_hours(self):
        screen, program, earner, other = households.two_adults_one_without_hours()

        arm = self.arm(screen, program, reported_hours_only(KsSnap))

        self.assertAlmostEqual(arm.hours_sent(earner.id), 1200 / 7.25 / 4)
        self.assertEqual(arm.hours_sent(other.id), 0)
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, earner.id))
        self.assertFalse(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, other.id))
        # Still eligible, and not zero — the unit shrinks to one person.
        self.assertTrue(arm.spm(probes.IsSnapEligibleProbe))
        # $72/mo, which is exactly what `TestRow2SalariedWorker` gets for a *single* adult on the
        # same $1,200/mo. That equality is the removal mechanism showing its work: the failing
        # adult is out of the unit size while their household's income still counts in full
        # (7 CFR 273.11(c)(1)), leaving a one-person unit at $1,200 — the same household row 2
        # already priced.
        self.assertEqual(arm.value(), 72 * 12)

    def test_shipped_keeps_both_adults_in_the_unit(self):
        screen, program, earner, other = households.two_adults_one_without_hours()

        arm = self.arm(screen, program, KsSnap)

        self.assertEqual(arm.hours_sent(other.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, other.id))
        # $320/mo for the intact two-person unit — 4.4x the floorless figure below it.
        self.assertEqual(arm.value(), 320 * 12)

    def test_control_denies_the_whole_unit(self):
        """With nothing sent, *both* adults read zero hours, so there is no passing member left to
        hold the unit together. This is the only shape that produces the stated $0."""
        screen, program, earner, other = households.two_adults_one_without_hours()

        arm = self.arm(screen, program, drop_hours(KsSnap))

        self.assertFalse(arm.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(arm.value(), 0)
