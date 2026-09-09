# MFB-1639 close-out — drafts

All three stubs are filed: MFB-1848 (county), MFB-1861 (TxCeap hours), MFB-1862 (work-test
exemptions). The comment is posted. Finding 5 stays on this branch only, by Kate's decision —
she wants to read it before it reaches MFB-1731.

## Comment for MFB-1639

**QA complete — the fix holds.** Evidence on branch `kate/mfb-1639-qa-snap-pe-frontier`
(`programs/programs/qa_mfb1639/`, commit `1ec295bb`): 51 tests, replayed from committed
cassettes. Sign-off record: `PE_FRONTIER_MATRIX_2026-09-08.md`.

**Run differently than written, on purpose.** The frontier-vs-current comparison this ticket
describes no longer exists — `GET /versions/us` returns `current` 1.821.2, `frontier` 1.821.10,
both past 1.815.1 where the 40-hour default was removed. The window closed Aug 26. So the matrix
ran against PE's private API pinned to **1.821.10**, and the "without the fix" arm was
reconstructed by dropping `SNAP_HOURS_INPUT` rather than by hunting a model that still carries the
old default — which also means the evidence stays reproducible after frontier moves again. A third
arm was added (hours sent, floor removed) because that is what isolates MFB-1637's *policy* choice
from the fix, which is what this ticket's "or intentionally differ per the hours-policy decision"
clause asks about.

**Result:** every household the hours change can reach is held at its pre-change value by the
40-hour floor, and the pre-fix payload reproduces the predicted false $0. MFB-1637's own live
4-case check is confirmed and extended to the full matrix.

**Three premises in the ticket no longer hold** — all three narrow the blast radius, and all three
predate the Aug 26 cutover:

1. PE's general 30-hour test **cannot deny**. `meets_snap_general_work_requirements` returns
   `exempted | compliant`, and `compliant` defaults True (changed 2026-07-08, before 1.815.1).
   Hours bite **only** through ABAWD.
2. A household member **under 14** is routed around ABAWD entirely. So row 4 as written ("youngest
   child 6+, parent not exempt") is protected — a child of 8 is as safe as a child of 3. Re-pointed
   to a 15-year-old to become probative.
3. ABAWD's exempt age is **65** post-HR1, not 60. Row 7 is fully exposed at 62, inert at 66; run at
   both.

**Rows 8 and 9 test something different than they look.** MA SNAP was never exposed on a
TAFDC-active screen — TAFDC needs a child, and a child under 14 skips ABAWD; the hours-class swap
earns its keep by keeping the screen to one request, not by changing a SNAP value. KS and NC have
no ABAWD waiver to interact with (PE ships no `waived_counties` entry for either).

**Four findings, in `FINDINGS.md`.** Three are latent behind the floor, which makes them
prerequisites for MFB-1731 rather than live bugs:

1. The pre-fix mode is **not only false $0** — a parent with a 15-year-old stays eligible and drops
   $546 → $298/mo, because PE removes the noncompliant member from the unit instead of zeroing it.
   A $0-vs-nonzero check passes this household. (Note, not a ticket.)
2. **No SNAP variant sends the county** the ABAWD waiver matches on, so it rides PE's
   alphabetically-first-county fallback — wrong in both directions (WA read as waived on
   `ADAMS_COUNTY_WA`; CO reads unwaived because its fallback is not on its own list). Dormant: all
   waived-county lists have lapsed, and the floor clears ABAWD anyway.
3. **TX CEAP declares no hours input** and is protected only by sharing SNAP's request — CEAP alone
   returns $0 where the shared request returns $1,200. This settles MFB-1640's open edge:
   `can_calc` cannot diverge (CEAP's dependencies are a strict subset of SNAP's, differing only by
   `age` and `household_size`), but three configuration routes can.
4. **`is_pregnant`, `unemployment_compensation` and `is_incapable_of_self_care`** decide SNAP's own
   work test, are collected by the screener, and are declared only by *other* programs. Pre-fix
   arm, same household: SNAP $0 alone vs $3,576 (pregnant) and $2,160 (unemployment) when WIC
   shares the request.

**WIC's knock-on is structurally unreachable** — every WIC category implies a member under 14 or a
pregnancy, both of which take the household out of ABAWD's reach; and `meets_wic_categorical_eligibility`
reads a take-up-gated `snap` that MFB already zeroes for non-reporters. The protection this ticket
credits to MFB-1637 came from **MFB-1312**.

Note: `policyengine-update-audit-2026-08-12.md`, cited here as living in mfb-repos, was not found
on any accessible surface (MFB-1640's session searched exhaustively; not repeated). Every claim
above is sourced from PE's own variables and parameters, MFB's code, and the recorded measurements.

---

## Ticket stub 1 — Send the county on SNAP requests

> **FILED as [MFB-1848](https://linear.app/myfriendben/issue/MFB-1848/send-the-county-on-snap-requests)**
> (2026-09-09, Backlog, label `PE`, blocks MFB-1731, related to MFB-1639). Body went in verbatim,
> as the reframed correctness point rather than a model-the-waiver request — which is what let it
> proceed alongside the standing decision to defer ABAWD county-waiver modelling.
> Do not re-file. Stubs 2 and 3 below remain unfiled.

**Blocks MFB-1731.** Label: PE.

`is_in_snap_abawd_waived_area` matches sub-state ABAWD waivers on `county_str`. No SNAP calculator
declares it — every variant sends only its state code — and PE's documentation for the variable
says a household with no county falls back to the first county alphabetically in its state. The
screener collects `Screen.county`, and `MoCountyDependency` shows we already send it elsewhere.

Measured at 2026-01 (last month WA's 38-county waiver was live), unemployed childless adult,
pre-fix payload, PE 1.821.10:

| State | Fallback county | Reads waived | Effect |
|---|---|---|---|
| WA | `ADAMS_COUNTY_WA` — on the list | Yes | False grant for every WA household |
| CO | `ADAMS_COUNTY_CO` — list begins at Alamosa | No | False denial for residents of waived counties |
| MA | Barnstable — list begins at Berkshire | No | Same false denial |
| IL | n/a, statewide via `state_code` | Yes | Correct |

Currently dormant twice over: every waived-county list has lapsed to `[]` (MA 2025-07-01,
CO 2025-10-01, WA 2026-02-01 — confirmed, a September run reads WA unwaived), and the 40-hour floor
satisfies ABAWD via `is_working` regardless. FNS approves waivers on a fiscal-year cycle, so the
lists refill. Evidence: `test_mfb1639_waived_area.py`.

**Ask:** should SNAP send `county_str` (as `MoCountyDependency` does), and is there a reason it was
left out that we should know about before changing it?

---

## Ticket stub 2 — TxCeap should declare the hours input it depends on

> **FILED as [MFB-1861](https://linear.app/myfriendben/issue/MFB-1861/txceap-should-declare-the-hours-input-it-depends-on)**
> (2026-09-09, cycle 13, Refinement, label `PE`, related to MFB-1639 and MFB-1640). Do not re-file.

Label: PE. Independent of MFB-1731 — reachable by configuration today.

`tx_ceap_eligible` reads `is_snap_eligible`, which PE gates on the SNAP work test. `TxCeap.pe_inputs`
contains no hours dependency, so CEAP's categorical pathway is protected only because
`calc_pe_eligibility` puts every calculator in one request and SNAP's hours ride along.

Measured (TX childless adult ~157% FPG, above CEAP's 150% limit but inside TX's 165% SNAP BBCE
limit — the only band where CEAP rides entirely on the SNAP branch):

- SNAP + CEAP in one request: **CEAP $1,200**
- CEAP alone: **CEAP $0**, no hours field in the payload

`can_calc` cannot produce that state — CEAP's screener dependencies are a strict subset of SNAP's,
the only SNAP-only ones being `age` and `household_size`. Three routes can:

1. `tx_snap` inactive or with a null `category` — `eligibility_results` builds `pe_calculators`
   from `active=True, category__isnull=False`.
2. A `Referrer.remove_programs` entry naming SNAP.
3. A `PolicyEngineConfig` pin below **1.779.3**: `_drop_unreadable_programs` drops SNAP because
   `snap_if_takes_up` carries `min_pe_version = (1, 779, 3)`, while `tx_ceap` is ungated.

Route 3 is the concerning one — one config field, fails silently, and CEAP's $0 is
indistinguishable from a genuine income-test denial. Evidence:
`test_mfb1639_shared_request.py::TestCeapWithoutSnapOnTheScreen`, `test_mfb1639_reachability.py`.

**Ask:** should `TxCeap` send the hours input itself, given it reads `is_snap_eligible`?

---

## Ticket stub 3 — SNAP does not send the work-test exemptions the screener collects

> **FILED as [MFB-1862](https://linear.app/myfriendben/issue/MFB-1862/snap-does-not-send-the-work-test-exemptions-the-screener-collects)**
> (2026-09-09, cycle 13, Refinement, label `PE`, blocks MFB-1731, related to MFB-1639 and
> MFB-1848). Do not re-file.

**Blocks MFB-1731.** Label: PE.

Three fields decide SNAP's own work test, are collected by the screener, and are declared by no
SNAP calculator:

| Field | Rule | Declared by |
|---|---|---|
| `is_pregnant` | ABAWD exemption, 7 U.S.C. 2015(o)(3)(E) | WIC |
| `unemployment_compensation` | 7 CFR 273.7(b)(1)(v), read by ABAWD via `is_snap_work_registration_exempt_non_age` | WIC income group |
| `is_incapable_of_self_care` | "caring for an incapacitated person", same variable | care-related programs only |

So the same household's SNAP answer depends on which siblings were on the screen. Pre-fix arm,
PE 1.821.10:

- Pregnant childless adult: SNAP **$0** alone → **$3,576** when WIC shares the request
- Childless adult on $600/mo unemployment: SNAP **$0** alone → **$2,160** with WIC

`is_incapable_of_self_care` is the sharpest: MFB already infers it from the same signals as
`is_disabled`, which SNAP *does* send, so the gap is which member the flag attaches to — not
missing data. `is_veteran` and `was_in_foster_care` are deliberately excluded: they are pre-HR1
exemptions only, applying post-2025-07-04 solely inside a good-faith window (Alaska), which MFB
does not serve.

Dormant today — the floor clears ABAWD via `is_working`, so no exemption is consulted. But
replacing the floor with real hours without these produces false denials for pregnant applicants,
unemployment recipients, and carers: three populations exempt by statute. Evidence:
`test_mfb1639_shared_request.py::TestSnapWorkExemptionsComeFromOtherPrograms`.

**Ask:** should these three go on `SNAP_BASE_INPUTS`, and should this be folded into stub 1 as one
"SNAP does not send the inputs its own work test reads" ticket with county as a fourth field?
