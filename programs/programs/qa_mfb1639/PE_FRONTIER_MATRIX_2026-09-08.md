# MFB-1639 — SNAP against the PolicyEngine frontier

**QA-only, TEMPORARY — not for production merge.**

Verdict: **the MFB-1637 fix holds.** Every household the hours change could reach is held at its
pre-change value by the 40-hour floor, and the pre-fix payload reproduces the false-$0 failure
mode the ticket predicted. Four findings came out of the matrix that the ticket did not anticipate;
three of them are latent rather than live, and all four are listed in `FINDINGS.md`.

## How this was run, and why not as written

| Ticket says | What was done |
|---|---|
| Compare `?pe_version=frontier` against `current`, Aug 19–25 | Not available. `GET /versions/us` on 2026-09-08 returns `current` 1.821.2, `frontier` 1.821.10 — both past 1.815.1, where the 40-hour default was removed. The window closed on Aug 26. |
| On staging | On PolicyEngine's private API (`household.api.policyengine.org/us/calculate`), pinned to **1.821.10**, the frontier version at time of recording. `PolicyEngineConfig.clean` rejects the floating aliases, so the pin is the exact number; every `min_pe_version` floor in `pe_dependencies/` is ≤ `(1, 779, 3)`, so gating at 1.821.10 sends the identical input set the `frontier` alias would have. |
| "Without the fix" arm | Reconstructed by dropping `SNAP_HOURS_INPUT` from `pe_inputs` rather than by finding a model that still carries the old default. Reproduces the pre-MFB-1637 request exactly and does not rot when frontier moves again. |
| — | A third arm was added: **floorless**, hours sent without the 40-hour floor. It is what isolates MFB-1637's *policy* choice from the *fix*, which is what the ticket's "or intentionally differ per the hours-policy decision" clause asks about. MFB-1731 owns the revisit. |

All values are annual dollars, the figure the screener reports. The date is pinned to
**2026-01-15**: `Snap.pe_period_month` reads today's month and it travels in the request body, so
a wall-clock month would move every figure (the maximum allotment steps up each October). The arms
differ only by the hours input, so no work-test verdict here depends on the month — with one
exception, called out in row 9, where the month decides which ABAWD waivers are in force.

Rows 1–7 are Kansas, a clean federal passthrough. FY2026 maximum allotments: $298 (one person),
$546 (two).

## Three premises in the ticket that no longer hold

These are why several rows are re-pointed rather than run as written. All three predate the
ticket's Aug 12 filing or landed before the cutover, and all three narrow the blast radius.

1. **The general 30-hour work test cannot deny.** `meets_snap_general_work_requirements` returns
   `exempted | compliant`, where `compliant = is_snap_work_program_participant |
   ~is_snap_work_registration_noncompliant` and the noncompliance flag defaults False.
   PolicyEngine made that change on **2026-07-08**, before 1.815.1. Measured: True for every
   member of every scenario here, in every arm, including with no hours sent at all. **Hours bite
   only through ABAWD.**
2. **A household member under 14 is routed around ABAWD entirely.**
   `meets_snap_work_requirements_person` returns `abawd & general` only when no household member
   is under the dependent-child threshold, which HR1 moved from 18 to **14**. With the general
   test unable to deny, any household containing someone under 14 is untouchable by the hours
   change. The ticket's row 4 ("youngest child 6+, parent not exempt") is therefore protected as
   written, and had to be re-pointed at 14 to become probative.
3. **ABAWD's exempt age is 65, not 60.** The bracket moved 50 → 51 → 53 → 55 → **65** on
   2025-07-04 (HR1). 60 exempts from the general test, which cannot deny. So the ticket's "60+
   adult" row is fully exposed at 62 and only inert at 66; it was run at both.

## The matrix

| # | Row | Household | shipped | control | floorless | Verdict |
|---|---|---|---|---|---|---|
| 1 | Working single adult, hourly | 30, $20/hr × **15 hrs** reported | **$564** (40 hrs sent) | **$0** | **$0** (15 hrs sent) | Fix holds. The only row where all three arms differ — the floor, not the fix, is what holds this household eligible |
| 2 | Working single adult, salaried | 30, $1,200/mo | **$864** (41.38 hrs) | **$0** | **$864** | Fix holds; floor inert (approximation already clears 20) |
| 3 | Unemployed childless adult (ABAWD) | 30, no income | **$3,576** (40 hrs) | **$0** | **$0** | Fix holds. **The row the policy decision rests on**: the floor asserts a work test is met for a household that reported no work |
| 4a | Youngest child 6+ *(as written)* | 40 + child **8** | $6,552 | **$6,552** | $6,552 | No movement. Premise stale — the under-14 gate skips ABAWD |
| 4b | Youngest child 14+ *(re-pointed)* | 40 + child **15** | **$6,552** | **$3,576** | $3,576 | Fix holds — but **not** as a false $0. See finding 1 |
| 5 | Child under 6 | 40 + child 3 | $6,552 | $6,552 | $6,552 | No movement; doubly exempt |
| 6 | Disabled adult | 40, `disabled=True` | $3,576 | $3,576 | $3,576 | No movement; `is_disabled` exempts from ABAWD |
| 7a | 60+ adult *(re-pointed to 62)* | 62, no income | **$3,576** | **$0** | **$0** | Fix holds. Premise stale — 62 is *not* ABAWD-exempt |
| 7b | 60+ adult *(re-pointed to 66)* | 66, no income | $3,576 | $3,576 | $3,576 | No movement; past the 65 exempt age |
| 8a | MA, SNAP alone, child under 14 | MA, 38 @ $20/hr × 15, child **4** | $5,328 | $5,328 | $5,328 | Swap works — one request, no split, all three programs sending the MA class. SNAP unexposed: a child under 14 skips ABAWD |
| 8b | MA, SNAP alone, dependent in the TAFDC/ABAWD gap | MA, 38 @ $20/hr × 15, child **15** | **$5,328** | **$2,352** | — | TAFDC's dependent limit is 18, ABAWD's is 14, so 14–17 falls in the gap. **Synthetic config** — see 8c |
| 8c | MA, **TAFDC active vs not** — the row as worded | same household as 8b, with `MaTafdc` + `MaEaedc` co-computed | $5,328 | **$5,328** | — | TAFDC and EAEDC declare the hours input themselves, so the pre-fix payload still carries hours and the parent stays. **On a TAFDC-active screen MA SNAP never moved.** What MFB-1637 bought MA is payload integrity, not SNAP values |
| 9 | KS/NC with county set | unemployed childless adult per state | — | KS **$0**, NC **$0**, CO **$0**, WA **$3,576**, IL **$3,576** | — | KS/NC have no waiver to interact with. WA read as waived on a county we never sent. See finding 2 |

### One failing adult

MFB-1637 states the impact as "one failing adult can zero out the household's SNAP". Run — the
ticket's matrix has no two-adult row — it is too strong. Two childless KS adults, one on $1,200/mo
and one reporting nothing:

| Arm | Value | What happens |
|---|---|---|
| shipped | **$3,840** ($320/mo) | Both hold, intact two-person unit |
| floorless | **$864** ($72/mo) | Only the adult without hours is removed; the unit shrinks to one person |
| control | **$0** | *Both* adults read zero hours, so no passing member is left to hold the unit |

The $864 is exactly row 2's figure for a *single* adult on the same $1,200/mo — the removal
mechanism showing its work, with the removed member's income still counted in full
(7 CFR 273.11(c)(1)). So the stated $0 needs *every* adult to fail; one failing adult produces a
partial loss with a plausible-looking number.

### The floor's cost to MA TAFDC — live, and the one thing here that is not dormant

MFB-1637 notes the floor "costs some accuracy on the field's three other readers (tx_ccs,
ma_tafdc, ma_eaedc all get more generous); accepted deliberately". Priced, on a MA parent with a
4-year-old, $20/hr × 15 hrs and $400/mo childcare:

| Arm | Hours read | TAFDC | SNAP |
|---|---|---|---|
| shipped | 40 (floored) | **$7,271** | $6,552 |
| floorless | 15 (reported) | **$0** | $6,552 |

`ma_tafdc_dependent_care_deduction_person` brackets the deduction on the SPM unit's total weekly
hours (106 CMR 704.275(A)) — $50 / $100 / $150 / $200 per month at 0 / 11 / 21 / 31+ hours. A
15-hour member read as 40 jumps two brackets, $100 → $200/mo against countable income.

Two things separate this from every other finding here. It is **live**: `MaTotalHoursWorkedDependency`
already fed TAFDC before MFB-1637, so PR 1725 moved MA TAFDC values in production for any
household reporting under 40 hours. And it runs in the **over-granting** direction, since the
regulation tiers the deduction on hours actually worked.

Two magnitude limiters. It is a **cliff, not a scaling** — this household sits on TAFDC's income
limit, so one bracket step crosses it. And the deduction is **capped at actual care expenses**
(`min_(total_amount, care_expenses)`), so a household with under $200/mo of care costs cannot see
the full bracket move; the example's $400/mo is above the cap, so it stands. Mechanism and
direction generalise, magnitude does not.

`tx_ccs` is affected by a confirmed path and remains unmeasured: `weekly_hours_worked` `adds`
`weekly_hours_worked_before_lsr`, and `tx_ccs_work_requirement_eligible` gates on 25 hours (one
non-exempt parent) or 50 (two or more) — which a floored 40 clears and a reported 15 fails.

### Knock-ons

| Program | Household | shipped | control | Verdict |
|---|---|---|---|---|
| **TX CEAP** | TX childless adult, ~157% FPG, $150/mo heating | SNAP $288, **CEAP $1,200** | SNAP $0, **CEAP $0** | **Exposed, and protected only by SNAP.** `tx_ceap_eligible` reads `is_snap_eligible`, which is not take-up-gated. Matches MFB-1640's $1,200 |
| **TX CEAP, alone** | same household, SNAP not on the screen | — | **CEAP $0** | MFB-1640's open edge, settled. See finding 3 |
| **TX WIC** | TX, 30 @ $1,200/mo + child 3 | SNAP $3,840, WIC $723 | SNAP $3,840, WIC $723 | **Structurally unreachable.** Every WIC category implies a member under 14 or a pregnancy, both of which take the household out of ABAWD's reach. Independently, `meets_wic_categorical_eligibility` reads a take-up-gated `snap` that MFB already zeroes for non-reporters (MFB-1312). The protection the ticket credits to MFB-1637 came from MFB-1312 |

## Does the verdict hold at the version production serves?

The matrix runs pinned to **frontier** (1.821.10), because that is what the ticket asked for. But
MFB-1637 records that we are "unpinned in both staging and production", and an unpinned request
sends the literal `current` alias — **1.821.2** on the day of recording, one release behind. So
every figure above is evidence about a model users are not on.

Checked rather than assumed. The decisive scenarios re-run pinned to `current` return **identical
values**: row 3 at $3,576 shipped / $0 pre-fix, the general test still unable to deny, and the
CEAP pair at $1,200 / $0. `test_mfb1639_current_version.py`. So the conclusions here can be stated
about production, not only about frontier.

## Test package

76 tests, all passing, replayed from committed cassettes at the pinned version
(`VCR_MODE=none`, which cannot record):

- `test_mfb1639_matrix.py` — 26 tests, rows 1–7 across three arms, plus the one-failing-adult case
- `test_mfb1639_shared_request.py` — 20 tests, rows 8a/8b/8c (MA), the floor's cost to TAFDC, the
  CEAP knock-on and CEAP-alone, the exemption-input coupling, and WIC
- `test_mfb1639_waived_area.py` — 6 tests, row 9 at January and September 2026
- `test_mfb1639_reachability.py` — 19 tests, static, no network
- `test_mfb1639_current_version.py` — 5 tests, the decisive scenarios re-run at `current` 1.821.2

Recorded with `PE_RECORD=1`; replay with `VCR_MODE=none .venv/bin/python -m pytest
programs/programs/qa_mfb1639 -n 0`. Re-recording is a deliberate act: PolicyEngine serves only
what `current`/`frontier` currently resolve to, so once it promotes past 1.821.10 these cassettes
return 422 `unsupported_version` rather than refreshing.

Nothing under `programs/programs/cross_white_label/`, `programs/framework/`, `integrations/` or
`screener/` was modified — `git diff origin/main` over those paths is empty.

## Missing context

`policyengine-update-audit-2026-08-12.md`, cited by both MFB-1637 and MFB-1639 as living "in
mfb-repos", does not exist on any accessible surface. MFB-1640's session searched the filesystem,
all three repos' git history, Google Drive, Linear documents, Slack, and `gh repo list` and did
not find it; that search was not repeated here. Every claim in this document is sourced from
PolicyEngine's own variables and parameters, MFB's code, and the measurements above.
