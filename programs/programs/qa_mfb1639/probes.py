"""MFB-1639 QA probes — TEMPORARY, not for production merge.

Diagnostic PolicyEngine *outputs*. MFB's calculators request only the variable a program
reports, so a $0 SNAP result carries no explanation of itself. These classes are added to a
calculator's ``pe_outputs`` (see ``harness.with_probes``) so the one request that computes the
household also returns the intermediates that decide it.

Adding outputs cannot change the answer: PolicyEngine computes the whole tree either way, and
the request's ``household`` inputs — the only thing that determines the result — are untouched.
That is what keeps the shipped arm's payload identical to production's.

Read straight off the private API rather than from the local ``policyengine-us`` checkout,
which is on 1.817.0 and would disagree with the pinned frontier leg.

Entity and period are PolicyEngine's, taken from the variable definitions:

  meets_snap_general_work_requirements Person,  MONTH
  meets_snap_abawd_work_requirements   Person,  MONTH
  meets_snap_work_requirements_person  Person,  MONTH
  is_in_snap_abawd_waived_area         Person,  MONTH
  is_snap_eligible                     SPMUnit, MONTH
  meets_wic_categorical_eligibility    Person,  MONTH
"""

from programs.framework.pe_dependencies.base import Member, SpmUnit


# There is deliberately NO probe for `weekly_hours_worked_before_lsr`, and adding one would
# corrupt the shipped arm. `_contributions` writes inputs and outputs through the same slot
# path, and an output class contributes `None` (the base `value()`), so a probe on a field we
# also *send* puts two distinct values in one slot — which `build_pe_input` resolves by
# SPLITTING the request into two payloads. The hours we sent are read out of the request body
# instead (`harness.hours_sent`), which is stronger evidence anyway: it is the wire value.


class MeetsSnapGeneralWorkRequirementsProbe(Member):
    """`exempted | compliant`, and `compliant` defaults True since PE's 2026-07-08 change —
    so this is expected True for everyone, hours or not."""

    field = "meets_snap_general_work_requirements"


class MeetsSnapAbawdWorkRequirementsProbe(Member):
    """The test that still denies on hours: needs >= 20 weekly hours or an exemption."""

    field = "meets_snap_abawd_work_requirements"


class MeetsSnapWorkRequirementsPersonProbe(Member):
    """Which route the member took. `abawd & general` when no household member is under the
    dependent-child threshold (14 post-HR1), `general` alone otherwise."""

    field = "meets_snap_work_requirements_person"


class IsInSnapAbawdWaivedAreaProbe(Member):
    """Reads `county_str`, which no SNAP variant sends — so this shows PolicyEngine's
    documented fallback (the alphabetically-first county in the state) at work."""

    field = "is_in_snap_abawd_waived_area"


class IsSnapEligibleProbe(SpmUnit):
    """What `tx_ceap_eligible` reads. Not take-up-gated, unlike `snap`."""

    field = "is_snap_eligible"


class MeetsWicCategoricalEligibilityProbe(Member):
    """`(snap + tanf > 0) | receives_snap | receives_tanf`. The `snap` term is take-up-gated,
    which is why the WIC knock-on is expected to be inert."""

    field = "meets_wic_categorical_eligibility"


#: Person-entity probes, all MONTH.
MEMBER_PROBES = [
    MeetsSnapGeneralWorkRequirementsProbe,
    MeetsSnapAbawdWorkRequirementsProbe,
    MeetsSnapWorkRequirementsPersonProbe,
    IsInSnapAbawdWaivedAreaProbe,
    MeetsWicCategoricalEligibilityProbe,
]

#: SPM-unit probes.
SPM_PROBES = [IsSnapEligibleProbe]

#: Every probe is defined per month and has to be requested there; asking for a MONTH variable
#: at the annual period returns its twelve months summed.
MONTHLY_PROBES = [
    MeetsSnapGeneralWorkRequirementsProbe,
    MeetsSnapAbawdWorkRequirementsProbe,
    MeetsSnapWorkRequirementsPersonProbe,
    IsInSnapAbawdWaivedAreaProbe,
    MeetsWicCategoricalEligibilityProbe,
    IsSnapEligibleProbe,
]

ALL_PROBES = MEMBER_PROBES + SPM_PROBES
