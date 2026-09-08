"""MFB-1639 — can a screen actually reach the states the knock-on findings need? TEMPORARY.

QA-only, not for production merge. No network: these are static facts about the calculators and
the code path that selects them, which is where the answers live.

MFB-1640 left one question open — whether `TxSnap.can_calc()` can be False while
`TxCeap.can_calc()` is True, which would leave CEAP reading `is_snap_eligible` with no hours in
the payload. It cannot. But `can_calc` is not the only thing that decides which calculators share
a request, and the other three routes are reachable by configuration.
"""

from django.test import TestCase

from integrations.clients.policyengine.registry import all_calculators
from programs.framework.pe_dependencies import member as member_dependency
from programs.programs.cross_white_label.liheap.tx import TxCeap
from programs.programs.cross_white_label.snap.tx import TxSnap
from programs.programs.cross_white_label.wic.tx import TxWic

HOURS_FIELD = "weekly_hours_worked_before_lsr"


def screener_dependencies(calculator) -> set:
    """Every screener field `can_calc` gates this calculator on.

    `PolicyEngineCalulator.can_calc` returns False if any `pe_inputs` entry names a missing
    dependency, then defers to the base class for the calculator's own `dependencies`.
    """
    names = set()
    for dependency in calculator.pe_inputs:
        names.update(getattr(dependency, "dependencies", ()) or ())
    names.update(getattr(calculator, "dependencies", ()) or ())
    return names


def sent_fields(calculator) -> set:
    return {dependency.field for dependency in calculator.pe_inputs}


class TestCeapCannotBeGatedApartFromSnapByCanCalc(TestCase):
    """MFB-1640's open edge, closed: `can_calc` cannot produce a screen with CEAP but not SNAP."""

    def test_ceap_dependencies_are_a_subset_of_snaps(self):
        self.assertTrue(screener_dependencies(TxCeap) <= screener_dependencies(TxSnap))

    def test_the_only_snap_only_dependencies_are_ones_every_screen_has(self):
        """So any screen that can calc CEAP can calc SNAP: a screen missing `age` or
        `household_size` has not been filled in at all, and would lose both programs."""
        snap_only = screener_dependencies(TxSnap) - screener_dependencies(TxCeap)

        self.assertEqual(snap_only, {"age", "household_size"})


class TestCeapDependsOnSnapForItsHours(TestCase):
    """Why the question mattered. CEAP reads `is_snap_eligible`, which PolicyEngine gates on the
    work test, but CEAP declares no hours input of its own — so its categorical pathway is only
    protected while a SNAP calculator is in the same request.

    Three routes still remove SNAP from a request that keeps CEAP, none of them `can_calc`:

      1. `eligibility_results` builds `pe_calculators` from programs with `active=True` and a
         non-null `category`. A `tx_snap` row that is inactive or uncategorised drops SNAP alone.
      2. A `Referrer.remove_programs` entry naming SNAP does the same for that referrer.
      3. `_drop_unreadable_programs` drops a calculator whose outputs the resolved PolicyEngine
         version cannot read. `snap_if_takes_up` carries `min_pe_version = (1, 779, 3)`; `tx_ceap`
         is ungated. A `PolicyEngineConfig` pin below 1.779.3 therefore drops SNAP and keeps CEAP.

    The behaviour that follows is measured in `test_mfb1639_shared_request`: CEAP alone returns $0
    where the shared request returns $1,200.
    """

    def test_ceap_sends_no_hours_of_its_own(self):
        self.assertNotIn(HOURS_FIELD, sent_fields(TxCeap))

    def test_snap_is_the_only_program_on_a_tx_screen_that_sends_hours(self):
        senders = sorted(
            code
            for code, calculator in all_calculators.items()
            if code.startswith("tx_") and HOURS_FIELD in sent_fields(calculator)
        )

        # tx_ccs sends hours too, so CEAP is incidentally protected on a screen where child care
        # applies — which is not a protection anyone chose, and does not apply to a childless
        # household, the only kind ABAWD can reach.
        self.assertEqual(senders, ["tx_ccs", "tx_snap"])

    def test_snap_output_is_version_gated_where_ceaps_is_not(self):
        """Route 3, as a fact about the classes rather than about a configuration."""
        snap_outputs = {output.field: output.min_pe_version for output in TxSnap.pe_outputs}
        ceap_outputs = {output.field: output.min_pe_version for output in TxCeap.pe_outputs}

        self.assertEqual(snap_outputs["snap_if_takes_up"], (1, 779, 3))
        self.assertEqual(ceap_outputs["tx_ceap"], ())


class TestSnapDoesNotSendItsOwnWorkExemptionInputs(TestCase):
    """The inverse coupling. Each field below is a PolicyEngine SNAP work-test exemption that the
    screener collects and that no SNAP calculator declares — so whether it reaches PolicyEngine
    depends on which sibling programs are on the screen. Benefit-level proof in
    `test_mfb1639_shared_request`.
    """

    def test_snap_does_not_send_is_pregnant(self):
        """An ABAWD exemption in its own right — 7 U.S.C. 2015(o)(3)(E)."""
        self.assertNotIn("is_pregnant", sent_fields(TxSnap))
        self.assertIn("is_pregnant", sent_fields(TxWic))

    def test_snap_does_not_send_unemployment_compensation(self):
        """Exempts from work registration under 7 CFR 273.7(b)(1)(v), which ABAWD reads through
        `is_snap_work_registration_exempt_non_age`. SNAP counts the money in the
        `snap_unearned_income` aggregate, which cannot carry what kind of money it is."""
        self.assertNotIn("unemployment_compensation", sent_fields(TxSnap))
        self.assertIn("unemployment_compensation", sent_fields(TxWic))

    def test_snap_does_not_send_is_incapable_of_self_care(self):
        """The "caring for an incapacitated person" exemption in the same variable. MFB already
        infers this field from the same signals as `is_disabled` — which SNAP *does* send — so the
        gap is which member the flag is attached to, not missing screener data."""
        self.assertNotIn("is_incapable_of_self_care", sent_fields(TxSnap))
        self.assertEqual(member_dependency.IsIncapableOfSelfCareDependency.field, "is_incapable_of_self_care")

    def test_no_snap_variant_sends_the_county_the_abawd_waiver_matches_on(self):
        """Row 9's root cause, as a static fact across every SNAP row."""
        snap_calculators = {
            code: calculator
            for code, calculator in all_calculators.items()
            if code.endswith("snap") or code.endswith("_fap")
        }

        self.assertTrue(snap_calculators)
        for code, calculator in snap_calculators.items():
            with self.subTest(program=code):
                self.assertNotIn("county_str", sent_fields(calculator))
                self.assertNotIn("county_fips", sent_fields(calculator))
