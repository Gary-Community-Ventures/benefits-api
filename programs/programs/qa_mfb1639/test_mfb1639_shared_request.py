"""MFB-1639 rows 8 and the knock-ons — what the shared PolicyEngine request couples. TEMPORARY.

QA-only, not for production merge.

`calc_pe_eligibility` builds ONE `pe_input` for every valid PolicyEngine calculator on a screen
and POSTs once. Every field any program declares is therefore visible to every other program's
rules. MFB-1637 relied on that on purpose — it put the hours input on SNAP and let TX CEAP read
the resulting `is_snap_eligible` from the same response.

The tests here run that coupling in both directions and find it is not only load-bearing but
under-specified: three inputs that decide SNAP's own work test are declared by *other* programs,
so the SNAP answer for one household depends on which siblings happened to be on the screen.

Each test is one (scenario, arm) pair and makes exactly one POST — see the matrix module's
docstring for why a cassette may hold only one PolicyEngine interaction.
"""

from datetime import date
from unittest.mock import patch

from programs.framework.pe_dependencies import member as member_dependency
from programs.programs.cross_white_label.liheap.tx import TxCeap
from programs.programs.cross_white_label.snap.ma import MaSnap
from programs.programs.cross_white_label.snap.tx import TxSnap
from programs.programs.cross_white_label.tanf.ma import MaTafdc
from programs.programs.cross_white_label.wic.tx import TxWic
from programs.programs.testing_fixtures.pe_integration import (
    PeIntegrationTestCase,
    add_income,
    add_member,
    make_program,
    make_screen,
)
from programs.programs.white_labels.ma.eaedc.calculator import MaEaedc
from programs.util import Dependencies
from screener.models import Expense

from programs.programs.qa_mfb1639 import probes
from programs.programs.qa_mfb1639.harness import (
    assert_single_payload,
    drop_hours,
    reported_hours_only,
    run_arm,
    run_shared,
)
from programs.programs.qa_mfb1639.test_mfb1639_matrix import FRONTIER_VERSION, TODAY

YEAR = "2026"
TX = {"white_label_code": "tx", "state_code": "TX", "zipcode": "78701", "county": "Travis County"}
MA = {"white_label_code": "ma", "state_code": "MA", "zipcode": "02101", "county": "Suffolk County"}


class SharedRequestTestCase(PeIntegrationTestCase):
    pe_version = FRONTIER_VERSION

    def pinned(self):
        patcher = patch("programs.programs.cross_white_label.snap.base.date")
        mock_date = patcher.start()
        mock_date.today.return_value = TODAY
        self.addCleanup(patcher.stop)


class TestRow8MassachusettsSharedRequest(SharedRequestTestCase):
    """Row 8 — "MA screen with TAFDC active vs. not (shared-request hours interaction)".

    Two findings, and neither is the one the row was written to look for.

    First, the swap works: MA SNAP, TAFDC and EAEDC share one request. MFB-1637's concern was
    that MA TAFDC/EAEDC approximate hours at the $15 state minimum wage while the base class uses
    the $7.25 federal floor, and two dependencies writing different values to one field cannot
    share a payload. `MaSnap` swaps the class rather than adding it, so the disagreement never
    arises.

    Second, the swap earns its keep by keeping the screen to one request, not by changing a SNAP
    value — and on a TAFDC-active screen MA SNAP was not exposed to the hours change at all. Two
    independent reasons cover it, and it took two corrections to get them both:

      * a household member under 14 is routed around ABAWD by
        `meets_snap_work_requirements_person`, and
      * `MaTafdc` and `MaEaedc` declare `MaTotalHoursWorkedDependency` themselves, so on any screen
        where they run the hours are in the shared payload whether SNAP declares them or not.

    The second is the one that actually covers TAFDC screens, because the first does not: TAFDC's
    dependent limit is 18 against ABAWD's 14, leaving a 14–17 gap. See
    `TestRow8MassachusettsTeenagerGap` for that gap and `TestRow8TafdcActiveVersusNot` for the
    sibling-hours rescue that closes it.
    """

    def ma_household(self):
        screen = make_screen(1639_08, household_size=2, **MA)
        parent = add_member(screen, 1639_08 * 10 + 1, "headOfHousehold", 30)
        add_income(parent, amount=20, income_type="wages", frequency="hourly")
        parent.income_streams.update(hours_worked=15)
        child = add_member(screen, 1639_08 * 10 + 2, "child", 4)
        return screen, parent, child

    def test_snap_tafdc_and_eaedc_share_one_request(self):
        """No network: `build_pe_input` decides this from the values alone.

        Asserted with teeth. `len(plan.buckets) == 1` would also hold if one of these programs
        contributed no hours value at all — through `can_calc` returning False, or through a
        refactor dropping the dependency — so the single-payload result would look like the
        mechanism working when it was really nothing to disagree about. All three are checked to
        declare the MA hours class first, and all three to be able to calc. `MaEaedc` matters
        as much as `MaTafdc` here: it sends the same class, so omitting it would cover less of
        the mechanism than the test appears to.
        """
        screen, parent, child = self.ma_household()
        specs = [
            (MaSnap, make_program("ma", "ma_snap", YEAR)),
            (MaTafdc, make_program("ma", "ma_tafdc", YEAR)),
            (MaEaedc, make_program("ma", "ma_eaedc", YEAR)),
        ]
        calculators = [cls(screen, program, Dependencies()) for cls, program in specs]

        for calculator in calculators:
            with self.subTest(calculator=type(calculator).__name__):
                declared = [
                    dependency
                    for dependency in type(calculator).pe_inputs
                    if dependency.field == "weekly_hours_worked_before_lsr"
                ]
                self.assertEqual(declared, [member_dependency.MaTotalHoursWorkedDependency])
                self.assertTrue(calculator.can_calc())

        assert_single_payload(screen, calculators)

    def test_ma_snap_sends_the_state_minimum_wage_variant(self):
        screen, parent, child = self.ma_household()
        self.pinned()
        program = make_program("ma", "ma_snap", YEAR)

        arm = run_arm(screen, MaSnap, program)

        # $20/hr x 15 reported hours, floored to 40 — MA's wage never enters, because the floor
        # is above what either wage would approximate for this member.
        self.assertEqual(arm.hours_sent(parent.id), 40)
        self.assertIn(member_dependency.MaTotalHoursWorkedDependency, MaSnap.pe_inputs)
        self.assertEqual(arm.value(), 5328)

    def test_ma_snap_is_unmoved_by_the_pre_fix_payload(self):
        """The child under 14 routes the parent around ABAWD, so dropping hours changes nothing."""
        screen, parent, child = self.ma_household()
        self.pinned()
        program = make_program("ma", "ma_snap", YEAR)

        arm = run_arm(screen, drop_hours(MaSnap), program)

        self.assertIsNone(arm.hours_sent(parent.id))
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(arm.value(), 5328)

    def test_ma_snap_is_unmoved_without_the_floor(self):
        screen, parent, child = self.ma_household()
        self.pinned()
        program = make_program("ma", "ma_snap", YEAR)

        arm = run_arm(screen, reported_hours_only(MaSnap), program)

        self.assertEqual(arm.hours_sent(parent.id), 15)
        self.assertEqual(arm.value(), 5328)


class TxCeapTestCase(SharedRequestTestCase):
    """A TX childless adult at ~157% FPG: above CEAP's own 150% income limit but inside Texas's
    165% SNAP BBCE limit. That band is the only one where CEAP's eligibility rides entirely on
    `is_snap_eligible`, which is what makes it the probe for the SNAP knock-on. Same household
    MFB-1640 used, and the $1,200 below is the figure it recorded."""

    def tx_household(self):
        screen = make_screen(1639_11, household_size=1, **TX)
        adult = add_member(screen, 1639_11 * 10 + 1, "headOfHousehold", 30)
        add_income(adult, amount=2_047, income_type="wages", frequency="monthly")
        Expense.objects.create(
            screen=screen, household_member=adult, type="heating", amount=150, frequency="monthly"
        )
        return screen, adult

    def specs(self, snap_class=TxSnap):
        """(specs, snap_class) — the class is handed back because `drop_hours` mints a fresh
        subclass on every call, and `run_shared` keys its results by the class it was given."""
        return [
            (snap_class, make_program("tx", "tx_snap", YEAR)),
            (TxCeap, make_program("tx", "tx_liheap", YEAR)),
        ], snap_class


class TestCeapKnockOn(TxCeapTestCase):
    def test_shipped_keeps_ceap_eligible(self):
        screen, adult = self.tx_household()
        self.pinned()

        specs, snap_class = self.specs()
        run = run_shared(screen, specs)

        self.assertTrue(run.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(run.value(snap_class), 288)
        self.assertEqual(run.value(TxCeap), 1_200)

    def test_control_takes_ceap_down_with_snap(self):
        """The knock-on the ticket predicts. `tx_ceap_eligible` reads `is_snap_eligible`, which is
        not take-up-gated, so a work-test denial removes CEAP's categorical pathway too."""
        screen, adult = self.tx_household()
        self.pinned()

        specs, snap_class = self.specs(drop_hours(TxSnap))
        run = run_shared(screen, specs)

        self.assertFalse(run.spm(probes.IsSnapEligibleProbe))
        self.assertEqual(run.value(snap_class), 0)
        self.assertEqual(run.value(TxCeap), 0)


class TestCeapWithoutSnapOnTheScreen(TxCeapTestCase):
    """MFB-1640's open edge, settled at the payload level.

    CEAP declares no hours dependency of its own — it is protected only because SNAP happens to
    put hours in the shared request. With SNAP absent, CEAP reads `is_snap_eligible` False and
    returns $0 for a household PolicyEngine would otherwise pay $1,200.

    `can_calc` cannot produce that state (see `test_mfb1639_reachability`), but three
    configuration routes can.
    """

    def test_ceap_alone_reads_zero(self):
        screen, adult = self.tx_household()
        ceap_program = make_program("tx", "tx_liheap", YEAR)

        calculator = TxCeap(screen, ceap_program, Dependencies())
        run = run_shared(screen, [(TxCeap, ceap_program)], probe_first=False)

        self.assertFalse(run.sent("weekly_hours_worked_before_lsr", adult.id))
        self.assertEqual(run.value(TxCeap), 0)


class TestSnapWorkExemptionsComeFromOtherPrograms(SharedRequestTestCase):
    """The inverse coupling, and the finding this ticket did not go looking for.

    Three inputs that decide SNAP's own work test are declared by other programs and by no SNAP
    calculator:

      `is_pregnant`                 an ABAWD exemption, 7 U.S.C. 2015(o)(3)(E). Declared by WIC.
      `unemployment_compensation`   feeds `is_snap_work_registration_exempt_non_age` via
                                    7 CFR 273.7(b)(1)(v). Declared by the WIC income group.
      `is_incapable_of_self_care`   the "caring for an incapacitated person" exemption in the
                                    same variable. Declared by care-related programs only.

    So the same household's SNAP answer depends on which sibling programs were on the screen.
    Shown here at benefit level in the pre-fix payload, where the work test is live. The shipped
    40-hour floor masks all of it today — every adult clears ABAWD on `is_working` regardless —
    which is precisely why it has to be fixed *before* the floor is revisited (MFB-1731).
    """

    def tx_screen(self, screen_id, **member_kwargs):
        screen = make_screen(screen_id, household_size=1, **TX)
        member = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 28, **member_kwargs)
        return screen, member

    def snap_only(self):
        """(specs, snap_class). The control class is returned rather than rebuilt: `drop_hours`
        mints a fresh subclass per call and `run_shared` keys results by identity."""
        snap_class = drop_hours(TxSnap)
        return [(snap_class, make_program("tx", "tx_snap", YEAR))], snap_class

    def snap_and_wic(self):
        snap_class = drop_hours(TxSnap)
        return [
            (snap_class, make_program("tx", "tx_snap", YEAR)),
            (TxWic, make_program("tx", "tx_wic", YEAR)),
        ], snap_class

    def test_pregnancy_exemption_is_lost_when_snap_runs_without_wic(self):
        screen, member = self.tx_screen(1639_12, pregnant=True)
        self.pinned()

        specs, snap_class = self.snap_only()
        run = run_shared(screen, specs)

        self.assertFalse(run.sent("is_pregnant", member.id))
        self.assertFalse(run.member(probes.MeetsSnapAbawdWorkRequirementsProbe, member.id))
        self.assertEqual(run.value(snap_class), 0)

    def test_pregnancy_exemption_applies_when_wic_shares_the_request(self):
        """Same household, same PolicyEngine version, $0 -> $3,576 because WIC sent one field."""
        screen, member = self.tx_screen(1639_12, pregnant=True)
        self.pinned()

        specs, snap_class = self.snap_and_wic()
        run = run_shared(screen, specs)

        self.assertTrue(run.sent("is_pregnant", member.id))
        self.assertTrue(run.member(probes.MeetsSnapAbawdWorkRequirementsProbe, member.id))
        self.assertEqual(run.value(snap_class), 298 * 12)

    def test_unemployment_exemption_is_lost_when_snap_runs_without_wic(self):
        screen, member = self.tx_screen(1639_13)
        add_income(member, amount=600, income_type="unemployment", frequency="monthly")
        self.pinned()

        specs, snap_class = self.snap_only()
        run = run_shared(screen, specs)

        self.assertFalse(run.sent("unemployment_compensation", member.id))
        self.assertFalse(run.member(probes.MeetsSnapAbawdWorkRequirementsProbe, member.id))
        self.assertEqual(run.value(snap_class), 0)

    def test_unemployment_exemption_applies_when_wic_shares_the_request(self):
        """$0 -> $2,160. SNAP counts this money (`snap_unearned_income`) but never tells
        PolicyEngine what kind of money it is, so the exemption it carries is invisible."""
        screen, member = self.tx_screen(1639_13)
        add_income(member, amount=600, income_type="unemployment", frequency="monthly")
        self.pinned()

        specs, snap_class = self.snap_and_wic()
        run = run_shared(screen, specs)

        self.assertTrue(run.sent("unemployment_compensation", member.id))
        self.assertTrue(run.member(probes.MeetsSnapAbawdWorkRequirementsProbe, member.id))
        self.assertEqual(run.value(snap_class), 2_160)


class TestWicKnockOnIsStructurallyUnreachable(SharedRequestTestCase):
    """The ticket's WIC knock-on: "PE-computed snap/tanf feed WIC categorical eligibility
    (CO/NC/MA/TX/MO)". It cannot fire, for two independent reasons.

    **Structural.** Every WIC category implies a household the work test cannot reach. INFANT and
    CHILD need a member under 5, POSTPARTUM and BREASTFEEDING imply an infant — all under the
    dependent-child threshold of 14, which routes the whole household around ABAWD. The only
    childless category is PREGNANT, and `is_pregnant` is both an ABAWD exemption and a field WIC
    itself puts in the shared request. So on any screen where WIC has a category to lose, SNAP's
    work test is already satisfied.

    **Contractual.** `meets_wic_categorical_eligibility` reads
    `(snap + tanf > 0) | receives_snap | receives_tanf`, and the `snap` term is gated on
    `takes_up_snap_if_eligible`, which MFB sends False for any household not reporting SNAP
    (MFB-1312's receipt contract). The simulated SNAP that a work-test denial would zero was
    already zero for those households; the branch that does fire reads *reported* receipt, which
    no PolicyEngine work rule touches.

    So the protection the ticket credits to MFB-1637 was already there, and came from MFB-1312.
    """

    def wic_household(self):
        """A parent and a 3-year-old: WIC category CHILD, and a member under 14."""
        screen = make_screen(1639_14, household_size=2, **TX)
        parent = add_member(screen, 1639_14 * 10 + 1, "headOfHousehold", 30)
        add_income(parent, amount=1_200, income_type="wages", frequency="monthly")
        child = add_member(screen, 1639_14 * 10 + 2, "child", 3)
        return screen, parent, child

    def specs(self, snap_class):
        return [
            (snap_class, make_program("tx", "tx_snap", YEAR)),
            (TxWic, make_program("tx", "tx_wic", YEAR)),
        ]

    def test_shipped(self):
        screen, parent, child = self.wic_household()
        self.pinned()

        run = run_shared(screen, self.specs(TxSnap))

        self.assertTrue(run.sent("weekly_hours_worked_before_lsr", parent.id))
        self.assertTrue(run.member(probes.MeetsWicCategoricalEligibilityProbe, child.id))
        self.assertEqual(run.value(TxSnap), 3_840)
        self.assertEqual(run.value(TxWic), 723)

    def test_control_moves_neither_snap_nor_wic(self):
        """The pre-fix payload. The child under 14 protects SNAP, so there is no denial for WIC to
        inherit — and WIC's categorical branch would not have read a denial anyway."""
        screen, parent, child = self.wic_household()
        self.pinned()
        snap_class = drop_hours(TxSnap)

        run = run_shared(screen, self.specs(snap_class))

        self.assertFalse(run.sent("weekly_hours_worked_before_lsr", parent.id))
        self.assertTrue(run.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertTrue(run.member(probes.MeetsWicCategoricalEligibilityProbe, child.id))
        self.assertEqual(run.value(snap_class), 3_840)
        self.assertEqual(run.value(TxWic), 723)


class TestRow8MassachusettsTeenagerGap(SharedRequestTestCase):
    """Row 8's exposed case, and a correction to the class above.

    "MA SNAP is never exposed on a TAFDC-active screen" is too strong. The two programs draw the
    dependent-child line in different places:

      TAFDC  `gov/states/ma/dta/tcap/tafdc/eligibility/age_limit/dependent.yaml` = **18**
             (`student_dependent.yaml` = 19), per 106 CMR 703.200 / 703.230
      ABAWD  `gov/usda/snap/work_requirements/abawd/age_threshold/dependent`, post-HR1 = **14**

    Those are PolicyEngine parameters, not asserted here: `policyengine_us` is not a benefits-api
    dependency, so a test importing it would not run in CI. The two tests below prove the gap
    behaviourally instead, which is the part that matters — the parent moves.

    So a TAFDC household whose youngest dependent is **14 to 17** qualifies for TAFDC and is *not*
    routed around ABAWD. Pre-fix, that parent fails the work test and is removed from the SNAP unit
    — the same partial loss as `TestRow4YoungestChildFourteenPlus`.

    **This runs `MaSnap` alone, which is a synthetic configuration.** With a 14–17 dependent, TAFDC
    is inside its own age limit, so it can calc and lands in the shared payload — carrying the
    hours that rescue the parent (`TestRow8TafdcActiveVersusNot`). Pre-fix exposure therefore
    needed the age gap *and* TAFDC/EAEDC absent from the request, which on a real MA screen means
    the same config routes as finding 3: an inactive or uncategorised program row, a
    `Referrer.remove_programs` entry, or a version pin that drops them.

    So the mechanism below is real and the exposure was narrow. It is kept because the mechanism is
    what a future work-test change would run into, not because MA users saw this.
    """

    def ma_teenager_household(self):
        screen = make_screen(1639_18, household_size=2, **MA)
        parent = add_member(screen, 1639_18 * 10 + 1, "headOfHousehold", 38)
        add_income(parent, amount=20, income_type="wages", frequency="hourly")
        parent.income_streams.update(hours_worked=15)
        # 15: a TAFDC dependent (under 18) who is over the ABAWD threshold (14).
        child = add_member(screen, 1639_18 * 10 + 2, "child", 15)
        return screen, parent, child

    def test_shipped_holds_the_parent_in_the_unit(self):
        screen, parent, child = self.ma_teenager_household()
        self.pinned()
        program = make_program("ma", "ma_snap", YEAR)

        arm = run_arm(screen, MaSnap, program)

        self.assertEqual(arm.hours_sent(parent.id), 40)
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(arm.value(), 5328)

    def test_control_removes_the_parent_from_the_unit(self):
        """The case the "never exposed" claim missed: pre-fix MA SNAP does move here."""
        screen, parent, child = self.ma_teenager_household()
        self.pinned()
        program = make_program("ma", "ma_snap", YEAR)

        arm = run_arm(screen, drop_hours(MaSnap), program)

        self.assertFalse(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertTrue(arm.member(probes.MeetsSnapWorkRequirementsPersonProbe, child.id))
        self.assertTrue(arm.spm(probes.IsSnapEligibleProbe))
        # $196/mo against the shipped $444/mo: the parent is out of the unit, and the household
        # keeps a plausible-looking 44% of its benefit rather than losing all of it.
        self.assertEqual(arm.value(), 2352)


class TestRow8TafdcActiveVersusNot(SharedRequestTestCase):
    """Row 8 as the ticket literally words it — "MA screen with TAFDC active vs. not
    (shared-request hours interaction)" — which the classes above never ran: they all call
    `run_arm` with `MaSnap` alone.

    Run properly, it inverts the reason MA was safe. `MaTafdc` and `MaEaedc` both declare
    `MaTotalHoursWorkedDependency` themselves, and one request carries every program on the
    screen. So on a TAFDC-active screen the hours are in the payload **whether or not SNAP
    declares them** — pre-fix MA SNAP was protected by its siblings, not by the child-age gate.

    Measured on the 14–17 household, the one case the child-age gate does *not* cover:

        SNAP alone,        pre-fix   $196/mo   parent removed from the unit
        SNAP + TAFDC/EAEDC, pre-fix  $444/mo   hours arrive from TAFDC; parent stays

    Which settles what MFB-1637 bought for MA: payload integrity (one request, no
    `DependencyError`, no 500), not SNAP values. A MA screen running TAFDC never saw the SNAP
    values move at all.
    """

    def teenager_household(self, screen_id):
        screen = make_screen(screen_id, household_size=2, **MA)
        parent = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 38)
        add_income(parent, amount=20, income_type="wages", frequency="hourly")
        parent.income_streams.update(hours_worked=15)
        child = add_member(screen, screen_id * 10 + 2, "child", 15)
        return screen, parent, child

    def specs(self, snap_class, with_siblings):
        specs = [(snap_class, make_program("ma", "ma_snap", YEAR))]
        if with_siblings:
            specs += [
                (MaTafdc, make_program("ma", "ma_tafdc", YEAR)),
                (MaEaedc, make_program("ma", "ma_eaedc", YEAR)),
            ]
        return specs

    def test_tafdc_not_active_pre_fix_removes_the_parent(self):
        screen, parent, child = self.teenager_household(1639_20)
        self.pinned()
        snap_class = drop_hours(MaSnap)

        run = run_shared(screen, self.specs(snap_class, with_siblings=False))

        self.assertFalse(run.sent("weekly_hours_worked_before_lsr", parent.id))
        self.assertFalse(run.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(run.value(snap_class), 2352)

    def test_tafdc_active_pre_fix_keeps_the_parent_via_its_own_hours_input(self):
        """The interaction the row is named after. SNAP sends nothing; TAFDC and EAEDC do."""
        screen, parent, child = self.teenager_household(1639_21)
        self.pinned()
        snap_class = drop_hours(MaSnap)

        run = run_shared(screen, self.specs(snap_class, with_siblings=True))

        self.assertTrue(run.sent("weekly_hours_worked_before_lsr", parent.id))
        self.assertTrue(run.member(probes.MeetsSnapWorkRequirementsPersonProbe, parent.id))
        self.assertEqual(run.value(snap_class), 5328)

    def test_tafdc_active_makes_no_difference_once_snap_sends_its_own_hours(self):
        """Post-fix the siblings are redundant for SNAP, which is the point of sending hours on
        SNAP itself: the value no longer depends on which programs share the screen."""
        screen, parent, child = self.teenager_household(1639_22)
        self.pinned()

        run = run_shared(screen, self.specs(MaSnap, with_siblings=True))

        self.assertEqual(run.value(MaSnap), 5328)


class TestFloorInflatesTheMaDependentCareDeduction(SharedRequestTestCase):
    """The cost MFB-1637 accepted and nobody priced.

    Its commit message notes the 40-hour floor "costs some accuracy on the field's three other
    readers (tx_ccs, ma_tafdc, ma_eaedc all get more generous); accepted deliberately". That
    reads as a rounding error. It is not.

    `ma_tafdc_dependent_care_deduction_person` sets the deduction from a bracket on the SPM
    unit's *total* weekly hours (106 CMR 704.275(A)), monthly, for a younger child:

        0–10 hrs → $50    11–20 → $100    21–30 → $150    31+ → $200

    So a member reporting 15 hours, read as the floored 40, jumps two brackets: $100 → $200/mo of
    deduction against countable income. Measured on a MA parent with a 4-year-old, $20/hr × 15
    hrs, and $400/mo of childcare — a household near TAFDC's income limit:

        floor (40 hrs)      TAFDC  $7,271/yr
        reported (15 hrs)   TAFDC  $0

    Unlike this ticket's other findings, **this one is live**, not latent behind the floor: the
    floor *is* the change. `MaTotalHoursWorkedDependency` already fed TAFDC before MFB-1637, so
    PR 1725 moved MA TAFDC values in production for any household reporting under 40 hours — and
    in the over-granting direction, since the regulation tiers the deduction on hours actually
    worked.

    The $0 → $7,271 magnitude is a cliff, not a scaling: this household sits on TAFDC's income
    limit, so one bracket step crosses it. A household far from the limit sees only the deduction
    change. What generalises is the mechanism and its direction, not the size.

    SNAP is unmoved here ($6,552 both arms) because the 4-year-old routes the household around
    ABAWD — which is what isolates the deduction as the only thing the floor is doing.
    """

    def childcare_household(self, screen_id):
        screen = make_screen(screen_id, household_size=2, **MA)
        parent = add_member(screen, screen_id * 10 + 1, "headOfHousehold", 38)
        add_income(parent, amount=20, income_type="wages", frequency="hourly")
        parent.income_streams.update(hours_worked=15)
        child = add_member(screen, screen_id * 10 + 2, "child", 4)
        Expense.objects.create(
            screen=screen, household_member=parent, type="childCare", amount=400, frequency="monthly"
        )
        return screen, parent, child

    def specs(self, floorless: bool):
        """All three calculators move together — the floor is the only variable."""
        unfloor = reported_hours_only if floorless else (lambda cls: cls)
        snap_class, tafdc_class, eaedc_class = unfloor(MaSnap), unfloor(MaTafdc), unfloor(MaEaedc)
        return [
            (snap_class, make_program("ma", "ma_snap", YEAR)),
            (tafdc_class, make_program("ma", "ma_tafdc", YEAR)),
            (eaedc_class, make_program("ma", "ma_eaedc", YEAR)),
        ], snap_class, tafdc_class

    def test_with_the_floor_tafdc_pays(self):
        screen, parent, child = self.childcare_household(1639_24)
        self.pinned()
        specs, snap_class, tafdc_class = self.specs(floorless=False)

        run = run_shared(screen, specs)

        self.assertEqual(run.value(tafdc_class), 7_271)
        self.assertEqual(run.value(snap_class), 6_552)

    def test_on_reported_hours_tafdc_pays_nothing(self):
        screen, parent, child = self.childcare_household(1639_25)
        self.pinned()
        specs, snap_class, tafdc_class = self.specs(floorless=True)

        run = run_shared(screen, specs)

        self.assertEqual(run.value(tafdc_class), 0)
        # SNAP is untouched, which is what makes the deduction the only moving part.
        self.assertEqual(run.value(snap_class), 6_552)
