"""MFB-1639 — does the verdict hold at the version users actually get? TEMPORARY.

QA-only, not for production merge.

The whole matrix runs pinned to **frontier** (1.821.10), because that is what the ticket asked
for. But MFB-1637 records that we are "unpinned in both staging and production", and an unpinned
request sends the literal `current` alias — 1.821.2 on the day these were recorded, one release
behind frontier. So every figure in the matrix is evidence about a model users are not on.

That gap is worth one check rather than an assumption. This module re-runs the decisive scenarios
pinned to `current` and asserts the same values the frontier arm produced:

  * the core SNAP claim (row 3: floor holds the household, pre-fix payload denies it)
  * the CEAP knock-on, which is the one cross-program consequence with a live config route

Identical figures across the two versions is the result that lets the matrix's conclusions be
stated about production rather than only about frontier.
"""

from datetime import date
from unittest.mock import patch

from programs.programs.cross_white_label.liheap.tx import TxCeap
from programs.programs.cross_white_label.snap.ks import KsSnap
from programs.programs.cross_white_label.snap.tx import TxSnap
from programs.programs.testing_fixtures.pe_integration import (
    PeIntegrationTestCase,
    add_income,
    add_member,
    make_program,
    make_screen,
)
from screener.models import Expense

from programs.programs.qa_mfb1639 import households, probes
from programs.programs.qa_mfb1639.harness import drop_hours, run_arm, run_shared
from programs.programs.qa_mfb1639.test_mfb1639_matrix import MAX_ALLOTMENT_ONE, TODAY

#: What `current` resolved to on 2026-09-08, when `frontier` was 1.821.10. This is the model an
#: unpinned production request actually gets.
CURRENT_VERSION = "1.821.2"

TX = {"white_label_code": "tx", "state_code": "TX", "zipcode": "78701", "county": "Travis County"}
YEAR = "2026"


class CurrentVersionTestCase(PeIntegrationTestCase):
    pe_version = CURRENT_VERSION

    def pinned(self):
        patcher = patch("programs.programs.cross_white_label.snap.base.date")
        mock_date = patcher.start()
        mock_date.today.return_value = TODAY
        self.addCleanup(patcher.stop)


class TestCoreSnapClaimHoldsAtCurrent(CurrentVersionTestCase):
    """Row 3 at `current`. Same figures as the frontier arm, so the 40-hour floor is doing the
    same work on the model production serves."""

    def test_shipped(self):
        screen, program, adult = households.unemployed_abawd(1639_30)
        self.pinned()

        with patch("programs.programs.cross_white_label.snap.base.date") as mock_date:
            mock_date.today.return_value = TODAY
            arm = run_arm(screen, KsSnap, program)

        self.assertEqual(arm.hours_sent(adult.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), MAX_ALLOTMENT_ONE * 12)

    def test_control(self):
        screen, program, adult = households.unemployed_abawd(1639_31)
        self.pinned()

        with patch("programs.programs.cross_white_label.snap.base.date") as mock_date:
            mock_date.today.return_value = TODAY
            arm = run_arm(screen, drop_hours(KsSnap), program)

        self.assertFalse(arm.member(probes.MeetsSnapAbawdWorkRequirementsProbe, adult.id))
        self.assertEqual(arm.value(), 0)

    def test_the_general_test_still_cannot_deny_at_current(self):
        """The 2026-07-08 change is in both versions, so hours bite only through ABAWD on the
        model production serves too — not just on frontier."""
        screen, program, adult = households.unemployed_abawd(1639_32)
        self.pinned()

        with patch("programs.programs.cross_white_label.snap.base.date") as mock_date:
            mock_date.today.return_value = TODAY
            arm = run_arm(screen, drop_hours(KsSnap), program)

        self.assertTrue(arm.member(probes.MeetsSnapGeneralWorkRequirementsProbe, adult.id))


class TestCeapKnockOnHoldsAtCurrent(CurrentVersionTestCase):
    """The CEAP knock-on at `current` — the cross-program consequence with a live route to it."""

    def tx_household(self, screen_id):
        screen = make_screen(screen_id, household_size=1, **TX)
        adult = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 30)
        add_income(adult, amount=2_047, income_type="wages", frequency="monthly")
        Expense.objects.create(
            screen=screen, household_member=adult, type="heating", amount=150, frequency="monthly"
        )
        return screen, adult

    def specs(self, snap_class, screen_id):
        return [
            (snap_class, make_program("tx", "tx_snap", YEAR)),
            (TxCeap, make_program("tx", "tx_liheap", YEAR)),
        ]

    def test_shipped_keeps_ceap_eligible(self):
        screen, adult = self.tx_household(1639_33)
        self.pinned()

        run = run_shared(screen, self.specs(TxSnap, 1639_33))

        self.assertTrue(run.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(run.value(TxSnap), 288)
        self.assertEqual(run.value(TxCeap), 1_200)

    def test_control_takes_ceap_down_too(self):
        screen, adult = self.tx_household(1639_34)
        self.pinned()
        snap_class = drop_hours(TxSnap)

        run = run_shared(screen, self.specs(snap_class, 1639_34))

        self.assertFalse(run.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(run.value(snap_class), 0)
        self.assertEqual(run.value(TxCeap), 0)
