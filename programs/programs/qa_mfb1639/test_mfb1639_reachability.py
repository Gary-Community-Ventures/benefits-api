"""MFB-1639 — can a screen actually reach the states the knock-on findings need? TEMPORARY.

QA-only, not for production merge. No network: these are static facts about the calculators and
the code path that selects them, which is where the answers live.

MFB-1640 left one question open — whether `TxSnap.can_calc()` can be False while
`TxCeap.can_calc()` is True, which would leave CEAP reading `is_snap_eligible` with no hours in
the payload. It cannot. But `can_calc` is not the only thing that decides which calculators share
a request, and the other three routes are reachable by configuration.
"""

from django.test import TestCase

from integrations.clients.policyengine import versions as pe_versions
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


class TestTheProductionHoursGuardHasAHole(TestCase):
    """`test_work_hours.py`'s `SNAP_VARIANTS` is a hardcoded dict, and `mo_snap` is not in it.

    That dict drives `test_every_snap_variant_sends_hours` and
    `test_every_snap_variant_sends_the_class_its_state_uses` — the guard that is supposed to
    ensure no SNAP row goes to PolicyEngine without hours. It lists eight rows plus MA; Missouri
    was added later (MFB-1637's own description enumerates "all seven state subclasses (CO, IL,
    KS, MA, NC, TX, WA)") and never joined it.

    Behaviour is fine: `MoSnap` splats `Snap.pe_inputs`, so it does send the base class. The hole
    is in the guard, and it is asymmetric — `TestOneHoursClassPerState` iterates the registry, so
    a *conflicting* hours class is caught for every program, but an *absent* one is only caught
    for the nine rows named in the dict. A ninth state added tomorrow that forgot to splat the
    parent's inputs would ship silently.

    The assertion below is the registry-driven form the guard should have taken. It is here rather
    than in the production suite because this package is not for merge; closing it properly means
    replacing that dict upstream.
    """

    def test_every_registered_snap_calculator_sends_exactly_one_hours_class(self):
        snap_calculators = {
            code: calculator
            for code, calculator in all_calculators.items()
            if code.endswith("snap") or code.endswith("_fap")
        }

        # Ten today: the federal base, eight states, and wa_fap.
        self.assertGreaterEqual(len(snap_calculators), 10)
        self.assertIn("mo_snap", snap_calculators)

        for code, calculator in snap_calculators.items():
            with self.subTest(program=code):
                declared = [dep for dep in calculator.pe_inputs if dep.field == HOURS_FIELD]
                self.assertEqual(len(declared), 1, f"{code} sends {len(declared)} hours inputs")

    def test_mo_snap_is_missing_from_the_production_guards_list(self):
        """Pins the hole itself, so adding `MoSnap` upstream turns this red and it can be deleted
        along with the finding."""
        from programs.programs.cross_white_label.snap.tests.test_work_hours import SNAP_VARIANTS
        from programs.programs.cross_white_label.snap.mo import MoSnap

        self.assertNotIn(MoSnap, SNAP_VARIANTS)


class TestCeapLosesSnapWhenPolicyEngineVersionsIsUnreachable(TestCase):
    """A fourth route to the CEAP-alone state, and the only one that is not a config mistake.

    `_drop_unreadable_programs` drops any calculator whose *output* the resolved model may not
    define. When there is no pin, the resolved version comes from `resolve_unpinned_comparable_version`,
    which returns None if `GET /versions/us` cannot be reached — and `version_supports` treats None
    as failing any minimum floor. `snap_if_takes_up` carries `min_pe_version = (1, 779, 3)`;
    `tx_ceap` is ungated.

    So if `/versions/us` is unavailable while `/calculate` is healthy, SNAP is dropped from every
    screen and CEAP is kept — reading `is_snap_eligible` with no hours in the payload, and
    returning $0 for households PolicyEngine would pay. Unlike routes 1–3 this needs no
    misconfiguration, is transient, and hits every screen at once rather than one referrer.

    The docstring on `_drop_unreadable_programs` names this condition itself; what it does not say
    is that CEAP survives the same request that loses SNAP.
    """

    def test_an_unresolved_version_withholds_snaps_output_but_not_ceaps(self):
        snap_output = {out.field: out.min_pe_version for out in TxSnap.pe_outputs}
        ceap_output = {out.field: out.min_pe_version for out in TxCeap.pe_outputs}

        self.assertEqual(snap_output["snap_if_takes_up"], (1, 779, 3))
        self.assertEqual(ceap_output["tx_ceap"], ())

        # None is what an unreachable /versions/us resolves to on an unpinned request.
        self.assertFalse(pe_versions.version_supports(None, (1, 779, 3), ()))
        self.assertTrue(pe_versions.version_supports(None, (), ()))


class TestVersionsOutageDropsSnapSsiAndTanfFromEveryScreen(TestCase):
    """The blast radius of the `/versions/us` route, measured rather than reasoned about.

    `TestCeapLosesSnapWhenPolicyEngineVersionsIsUnreachable` above frames this as a CEAP problem.
    That framing is too narrow: CEAP reading $0 is a *downstream symptom* of a screen-wide
    failure.

    `_drop_unreadable_programs` drops every program whose output the resolved model may not
    define, and MFB-1312's receipt contract made the `*_if_takes_up` outputs the first gated ones
    in the codebase. With `comparable_version` None, that is **16 of 133 registered calculators**,
    across the three largest cash-and-food families:

        snap_if_takes_up   10 rows — the federal base, seven states, MO, and wa_fap
        ssi_if_takes_up     5 rows — the federal base plus KS, MO, TX, WA
        tanf_if_takes_up    1 row  — federal tanf

    So while `/versions/us` is unavailable and `/calculate` is healthy, SNAP, SSI and federal TANF
    disappear from every screen in every state, and the other 117 programs compute as though those
    households receive none of them. CEAP's $0 follows because dropping SNAP also removes SNAP's
    inputs — including the hours — from the payload the surviving programs share.

    Two timing details bound it. `_fetch_pe_versions` caches success for an hour
    (`_PE_VERSIONS_CACHE_TTL = 3600`) and deliberately does **not** cache failures, so an outage
    bites only once the last good entry expires, and then bites every request until PE recovers.
    `_drop_unreadable_programs` emits a `capture_message`, so this is visible in Sentry rather
    than silent — but the served result is an ordinary screen with three major programs missing.
    """

    def dropped_when_unresolved(self):
        dropped = {}
        for code, calculator in all_calculators.items():
            unsupported = [
                output.field
                for output in calculator.pe_outputs
                if not pe_versions.version_supports(
                    None,
                    getattr(output, "min_pe_version", ()),
                    getattr(output, "max_pe_version", ()),
                )
            ]
            if unsupported:
                dropped[code] = unsupported
        return dropped

    def test_the_drop_set_is_snap_ssi_and_tanf(self):
        dropped = self.dropped_when_unresolved()

        fields = {field for fields in dropped.values() for field in fields}
        self.assertEqual(fields, {"snap_if_takes_up", "ssi_if_takes_up", "tanf_if_takes_up"})

    def test_every_snap_row_is_dropped_not_merely_the_one_ceap_rides_on(self):
        dropped = self.dropped_when_unresolved()

        snap_rows = {code for code in all_calculators if code.endswith("snap") or code.endswith("_fap")}
        self.assertTrue(snap_rows <= set(dropped), snap_rows - set(dropped))
        self.assertGreaterEqual(len(snap_rows), 10)

    def test_ceap_itself_survives_the_request_that_loses_them(self):
        """Which is what turns a missing-programs outage into a wrong *number* for CEAP."""
        dropped = self.dropped_when_unresolved()

        self.assertNotIn("tx_liheap", dropped)
        self.assertIn("tx_snap", dropped)

    def test_the_failure_is_reported_rather_than_silent(self):
        """`_drop_unreadable_programs` calls `capture_message`, so Sentry sees it. The finding is
        about the served result, not about observability."""
        import inspect

        from integrations.clients.policyengine import policy_engine

        source = inspect.getsource(policy_engine._drop_unreadable_programs)
        self.assertIn("capture_message", source)
