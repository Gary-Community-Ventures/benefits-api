"""MFB-1639 QA harness — TEMPORARY, not for production merge.

Runs one MFB SNAP calculator against one household in two arms, both against the same pinned
PolicyEngine version on the private API (`household.api.policyengine.org`):

  shipped   `pe_inputs` exactly as they are on `origin/main` — hours sent, floored at 40 for
            members 16 and over (MFB-1637).
  control   the same calculator with the hours dependency filtered out of `pe_inputs`. This
            reproduces the pre-MFB-1637 payload, and so the false-$0 failure mode, without
            needing a PolicyEngine version that still carries the old 40-hour default. The
            ticket's `?pe_version=frontier` vs `current` comparison is no longer available:
            both aliases have promoted past 1.815.1, where the default was removed.

Reconstructing the control from our own payload rather than from an old model is also what
keeps this evidence from rotting — it stays reproducible after frontier moves again.

Diagnostics come back from the same request via `probes`, not from the local `policyengine-us`
checkout (1.817.0), which would disagree with the pinned leg.
"""

from dataclasses import dataclass
from typing import Optional

from integrations.clients.policyengine.engines import PrivateApiSim
from programs.framework.base import Eligibility
from programs.framework.pe_dependencies import member as member_dependency
from programs.framework.pe_dependencies.payload import build_pe_input, pe_input
from programs.util import Dependencies
from screener.models import Screen

from programs.programs.qa_mfb1639 import probes

HOURS_FIELD = "weekly_hours_worked_before_lsr"

#: Both hours classes. The control has to drop whichever one its state sends — MA swaps in the
#: $15-minimum-wage variant rather than adding it, so filtering only the base class would leave
#: MA's arm identical to shipped and silently produce a no-op "control".
HOURS_CLASSES = (
    member_dependency.TotalHoursWorkedDependency,
    member_dependency.MaTotalHoursWorkedDependency,
)


def drop_hours(calculator_class: type) -> type:
    """`calculator_class` with every hours dependency removed from `pe_inputs`.

    Subclassed rather than mutated: `pe_inputs` is a class attribute shared by the registry,
    and editing it in place would leak the control arm into every other test in the process.
    """
    kept = [dep for dep in calculator_class.pe_inputs if dep not in HOURS_CLASSES]

    if len(kept) == len(calculator_class.pe_inputs):
        raise AssertionError(
            f"{calculator_class.__name__} sends no hours dependency, so there is nothing for the "
            "control arm to drop and both arms would be identical."
        )

    return type(f"NoHours{calculator_class.__name__}", (calculator_class,), {"pe_inputs": kept})


def reported_hours_only(calculator_class: type) -> type:
    """`calculator_class` sending hours, but without the 40-hour floor.

    A third arm, and the one that isolates the *policy* decision from the *fix*. MFB-1637 chose
    a 40-hour floor for every member 16 and over — PolicyEngine's own suggested no-op — over
    sending the hours the screen actually evidences. Dropping only the floor shows what the
    alternative would have produced, which is what the ticket means by results that
    "intentionally differ per the MFB-1637 hours-policy decision". MFB-1731 owns the revisit.

    `assumed_weekly_hours = 0` makes `value()`'s `max(reported, assumed)` return `reported`.
    """
    swapped = []
    for dep in calculator_class.pe_inputs:
        if dep in HOURS_CLASSES:
            swapped.append(type(f"Floorless{dep.__name__}", (dep,), {"assumed_weekly_hours": 0}))
        else:
            swapped.append(dep)

    if swapped == list(calculator_class.pe_inputs):
        raise AssertionError(f"{calculator_class.__name__} sends no hours dependency to unfloor.")

    return type(f"Floorless{calculator_class.__name__}", (calculator_class,), {"pe_inputs": swapped})


def with_probes(calculator_class: type) -> type:
    """`calculator_class` with the diagnostic outputs appended.

    Only `pe_outputs` grows, so the `household` inputs — the whole of what decides the result —
    are untouched, and the shipped arm's request body stays production's. PolicyEngine computes
    the same tree either way; this just asks it to return more of it.
    """
    return type(
        f"Probed{calculator_class.__name__}",
        (calculator_class,),
        {
            "pe_outputs": [*calculator_class.pe_outputs, *probes.ALL_PROBES],
            "pe_monthly_outputs": [*calculator_class.pe_monthly_outputs, *probes.MONTHLY_PROBES],
        },
    )


@dataclass
class Arm:
    """One (calculator, household) run: what we sent, and everything PolicyEngine returned.

    The periods are snapshotted rather than read back off the calculator. `Snap.pe_period_month`
    reads `date.today()`, so a test that pins the date while building the request would resolve a
    *different* month when reading the response — the request says `2026-01` and the read asks
    for `2026-09`. Capturing them inside the same patched block keeps the two halves agreeing.
    """

    calculator: object
    eligibility: Eligibility
    sim: PrivateApiSim
    payload: dict
    annual_period: str
    month_period: str

    def value(self) -> int:
        """The whole-dollar annual figure the screener would report."""
        import math

        return math.trunc(self.eligibility.value)

    def hours_sent(self, member_id: int) -> Optional[float]:
        """The hours value in the *request body* for this member, or None if none was sent.

        Read off the wire rather than probed back: a probe on a field we also send would put a
        `None` in the same slot as the sent value and split the request (see `probes`).
        """
        periods = self.payload["household"]["people"][str(member_id)].get(HOURS_FIELD)

        if periods is None:
            return None

        if len(periods) != 1:
            raise AssertionError(f"{HOURS_FIELD} written at more than one period: {periods}")

        return next(iter(periods.values()))

    def member(self, probe: type, member_id: int):
        """A person-entity probe's value for one member."""
        return self.sim.value("people", str(member_id), probe.field, self.month_period)

    def spm(self, probe: type):
        """An spm_unit-entity probe's value."""
        return self.sim.value("spm_units", "spm_unit", probe.field, self.month_period)

    def snap_monthly(self) -> float:
        """`snap_if_takes_up` at the month SNAP is read at — the figure `household_value`
        annualizes."""
        return self.sim.value("spm_units", "spm_unit", "snap_if_takes_up", self.month_period)


def run_arm(screen: Screen, calculator_class: type, program, probe: bool = True) -> Arm:
    """Build one payload, POST once, and return the calculator's Eligibility plus the sim.

    Mirrors `pe_integration.calc_pe_program` — deliberately not `calc_pe_eligibility`, which
    swallows every exception and would turn a cassette miss into an empty dict — but keeps the
    sim so the diagnostics requested alongside the headline can be read back.
    """
    if probe:
        calculator_class = with_probes(calculator_class)

    calculator = calculator_class(screen, program, Dependencies())

    if not calculator.can_calc():
        raise AssertionError(
            f"{calculator_class.__name__} cannot calc for this screen, so production would omit "
            "the program rather than call PolicyEngine."
        )

    payload = pe_input(screen, [calculator])
    sim = PrivateApiSim(payload)
    calculator.set_engine(sim)

    return Arm(
        calculator=calculator,
        eligibility=calculator.calc(),
        sim=sim,
        payload=payload,
        annual_period=calculator.pe_period,
        month_period=calculator.pe_month_period,
    )


@dataclass
class SharedRun:
    """Several programs answered by ONE PolicyEngine request, as production does it.

    `calc_pe_eligibility` builds a single `pe_input` for every valid PE calculator on a screen
    and POSTs once, so a field one program declares is visible to every other program's rules.
    That coupling is the subject of half this ticket's findings, and it cannot be reproduced by
    running calculators one at a time.
    """

    eligibility: dict
    sim: PrivateApiSim
    payload: dict
    month_period: str

    def value(self, calculator_class: type) -> int:
        import math

        return math.trunc(self.eligibility[calculator_class].value)

    def member(self, probe: type, member_id: int):
        return self.sim.value("people", str(member_id), probe.field, self.month_period)

    def spm(self, probe: type):
        return self.sim.value("spm_units", "spm_unit", probe.field, self.month_period)

    def sent(self, field: str, member_id: int) -> bool:
        """Whether `field` appears in the request body for this member at all."""
        return field in self.payload["household"]["people"][str(member_id)]


def run_shared(screen: Screen, calc_specs, probe_first: bool = True) -> SharedRun:
    """Run several calculators through one shared payload and one POST.

    `calc_specs` is a list of (calculator_class, program) pairs. The first is probed, so the
    diagnostics come back keyed to whichever program the scenario is about. Results are keyed by
    the class as passed in, not by the probed subclass.
    """
    calculators = {}
    instances = []
    for index, (cls, program) in enumerate(calc_specs):
        runtime = with_probes(cls) if (probe_first and index == 0) else cls
        instance = runtime(screen, program, Dependencies())
        if not instance.can_calc():
            raise AssertionError(f"{cls.__name__} cannot calc for this screen.")
        calculators[cls] = instance
        instances.append(instance)

    payload = pe_input(screen, instances)
    sim = PrivateApiSim(payload)

    eligibility = {}
    for cls, instance in calculators.items():
        instance.set_engine(sim)
        eligibility[cls] = instance.calc()

    return SharedRun(
        eligibility=eligibility,
        sim=sim,
        payload=payload,
        month_period=instances[0].pe_month_period,
    )


def assert_single_payload(screen: Screen, calculators) -> None:
    """Assert these programs share one PolicyEngine request.

    `build_pe_input` answers programs that disagree about a field with a follow-up request
    rather than raising, so a regression here is a silent extra round trip (it used to be a
    500). Used by the MA row, where SNAP, TAFDC and EAEDC all read the hours field.
    """
    plan = build_pe_input(screen, calculators)

    if len(plan.buckets) != 1:
        raise AssertionError(
            f"expected one payload, got {len(plan.buckets)}; conflicts: {plan.conflicts}"
        )
