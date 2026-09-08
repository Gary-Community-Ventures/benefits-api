# MFB-1639 — findings and follow-ups

**QA-only, TEMPORARY — not for production merge.** Sign-off record:
`PE_FRONTIER_MATRIX_2026-09-08.md`. Nothing here was fixed in this session.

Headline: **MFB-1637 holds.** Four findings came out of the matrix. One is a correction to how the
pre-fix failure mode was characterised; three are latent defects that the 40-hour floor currently
masks, which makes them prerequisites for **MFB-1731** (revisit the floor) rather than live bugs.
That is the reason to file them now: the floor is the only thing holding them shut, and MFB-1731
is the ticket that opens it.

---

## 1. The pre-fix failure mode was not only false $0 — it silently halves mixed households

**Verified.** `test_mfb1639_matrix.py::TestRow4YoungestChildFourteenPlus`,
`::TestOneFailingAdultDoesNotZeroTheHousehold`, and
`test_mfb1639_shared_request.py::TestRow8MassachusettsTeenagerGap`.

A household of a parent and a 15-year-old, pre-fix payload: SNAP stays **eligible** and drops from
**$546/mo to $298/mo** — the two-person allotment to the one-person allotment. PolicyEngine
removes a work-test-noncompliant member from the SNAP unit rather than zeroing the unit
(`is_snap_work_registration_noncompliant`: "removed from the SNAP unit size"), and the remaining
child keeps the unit eligible. The same thing happens in MA at $444/mo → $196/mo where the
youngest dependent is 15.

**MFB-1637's own framing is too strong.** It states the impact as "one failing adult can zero out
the household's SNAP". Two childless adults, one on $1,200/mo and one reporting nothing:

| Arm | Value | What happens |
|---|---|---|
| shipped | $3,840 | Both hold |
| floorless | **$864** | Only the adult without hours is removed; unit shrinks to one person |
| control | **$0** | *Both* read zero hours, so no passing member is left |

$864 is exactly what a *single* adult on the same $1,200/mo receives, with the removed member's
income still counted in full (7 CFR 273.11(c)(1)). So the stated $0 needs **every** adult to fail.
One failing adult is a partial loss.

Why it matters: a QA check written against the ticket's stated expectation — "expect false $0 SNAP
results" — passes every one of these households. Any future work-test regression in a household
that retains one qualifying member will present as a plausible-looking smaller number, not a zero.

**Not a defect in MFB code, and nothing to file.** Recorded so the next person testing this area
does not write a $0-vs-nonzero assertion and believe it covers the case.

---

## 2. No SNAP variant sends the county the ABAWD waiver matches on

**Verified.** `test_mfb1639_waived_area.py`, and statically for every SNAP row in
`test_mfb1639_reachability.py::...::test_no_snap_variant_sends_the_county_the_abawd_waiver_matches_on`.

`is_in_snap_abawd_waived_area` matches sub-state waivers on `county_str`. No SNAP calculator
declares it — every variant sends only its state code — and PolicyEngine's own documentation for
the variable says a household with no county falls back to **the first county alphabetically in
its state**. The screener does collect `Screen.county`, and `MoCountyDependency` shows we already
know how to send it.

Measured at January 2026, the last month Washington's 38-county waiver was live:

| State | Waived list | Fallback county | Reads waived? | Consequence |
|---|---|---|---|---|
| WA | 38 counties | `ADAMS_COUNTY_WA` — **on the list** | **Yes** | False grant: every WA household read as waived wherever they lived |
| CO | list begins at Alamosa | `ADAMS_COUNTY_CO` — not on it | No | False denial: residents of genuinely waived CO counties read as unwaived |
| MA | list begins at Berkshire | Barnstable — not on it | No | Same false denial |
| KS, NC | no list at all | — | No | Correct; nothing to interact with |
| IL | statewide, matched on `state_code` | n/a | **Yes** | Correct, for the right reason |

**Currently dormant, twice over.** Every waived-county list has lapsed to `[]`
(MA 2025-07-01, CO 2025-10-01, WA 2026-02-01) — confirmed at September 2026, where WA now reads
unwaived — and the shipped 40-hour floor satisfies ABAWD via `is_working` regardless. FNS approves
waivers on a fiscal-year cycle, so the lists will refill.

**File:** send the county on SNAP requests. Blocks MFB-1731. Sub-state waivers are the only ABAWD
lever the screener already has the data for, and the fallback is wrong in both directions, so this
cannot be left to be discovered by whoever removes the floor.

---

## 3. TX CEAP's categorical pathway depends on SNAP being on the same screen

**Verified.** `test_mfb1639_shared_request.py::TestCeapWithoutSnapOnTheScreen` and
`test_mfb1639_reachability.py`. This settles the edge MFB-1640 recorded as unconfirmed.

`tx_ceap_eligible` reads `is_snap_eligible`, which PolicyEngine gates on the work test. `TxCeap`
declares **no hours input of its own** — it is protected only because `calc_pe_eligibility` puts
every calculator in one request, so SNAP's hours ride along. Measured: the shared request returns
**CEAP $1,200**; CEAP alone returns **$0** for the same household, with no hours field in the
payload.

MFB-1640's specific question — can `TxSnap.can_calc()` be False while `TxCeap.can_calc()` is True?
— is **no**. CEAP's screener dependencies are a strict subset of SNAP's, and the only SNAP-only
dependencies are `age` and `household_size`, which any screen that can calc CEAP also has.

Three other routes do produce that state, none of them `can_calc`:

1. `eligibility_results` builds `pe_calculators` from programs with `active=True` and a non-null
   `category`. A `tx_snap` row that is inactive or uncategorised drops SNAP alone.
2. A `Referrer.remove_programs` entry naming SNAP does the same for that referrer.
3. `_drop_unreadable_programs` drops a calculator whose outputs the resolved PolicyEngine version
   cannot read. `snap_if_takes_up` carries `min_pe_version = (1, 779, 3)`; `tx_ceap` is ungated. A
   `PolicyEngineConfig` pin below 1.779.3 drops SNAP and keeps CEAP.

Route 3 is the one to worry about: it is a single config field, it fails silently, and CEAP's $0
is indistinguishable from a genuine income-test denial.

**File:** `TxCeap` should send the hours input itself rather than depending on a sibling. It reads
`is_snap_eligible`, so it owns that dependency. Note `tx_ccs` also sends hours, which incidentally
protects CEAP on child-care screens — but not for a childless household, the only kind ABAWD
reaches.

---

## 4. Three SNAP work-test exemptions are declared by other programs and by no SNAP calculator

**Verified at benefit level.**
`test_mfb1639_shared_request.py::TestSnapWorkExemptionsComeFromOtherPrograms`.

The same coupling as finding 3, running the other way. These fields decide SNAP's own work test,
the screener collects all three, and no SNAP calculator sends any of them:

| Field | Rule | Declared by |
|---|---|---|
| `is_pregnant` | ABAWD exemption, 7 U.S.C. 2015(o)(3)(E) | WIC |
| `unemployment_compensation` | Work-registration exemption, 7 CFR 273.7(b)(1)(v), read by ABAWD through `is_snap_work_registration_exempt_non_age` | the WIC income group |
| `is_incapable_of_self_care` | "Caring for an incapacitated person", same variable | care-related programs only |

So the same household gets a different SNAP answer depending on which siblings were on the screen.
Measured in the pre-fix arm, where the work test is live:

- Pregnant childless adult: SNAP **$0** alone → **$3,576** when WIC shares the request.
- Childless adult on $600/mo unemployment: SNAP **$0** alone → **$2,160** with WIC.

`is_incapable_of_self_care` is the sharpest of the three: MFB already infers it from the same
signals as `is_disabled`, which SNAP *does* send, so the gap is only which member the flag is
attached to — not missing screener data.

Two nearby fields are deliberately **not** findings: `is_veteran` and `was_in_foster_care` are
pre-HR1 ABAWD exemptions only, and post-2025-07-04 they apply solely inside a good-faith-effort
window (currently Alaska), which MFB does not serve.

**Currently dormant** — the floor clears ABAWD via `is_working` for every adult, so no exemption
is consulted. **File:** send `is_pregnant`, `unemployment_compensation` and
`is_incapable_of_self_care` on SNAP requests. Blocks MFB-1731. Without them, replacing the floor
with real hours produces false denials for pregnant applicants, unemployment recipients, and
carers — three populations that are exempt by statute.

---

## Follow-up tickets to file

| Finding | Ask | Relationship |
|---|---|---|
| 2 | Send `county_str` on SNAP requests so `is_in_snap_abawd_waived_area` stops riding an alphabetical fallback | Blocks MFB-1731 |
| 3 | `TxCeap` should declare the hours input it depends on | Independent; fixes a silent $0 reachable by config today |
| 4 | Send `is_pregnant`, `unemployment_compensation`, `is_incapable_of_self_care` on SNAP requests | Blocks MFB-1731 |

Finding 1 is a note, not a ticket.

Findings 2 and 4 are the same shape and could reasonably be one ticket — "SNAP does not send the
inputs its own work test reads" — with the county as its fourth field. Filed separately here
because the county has a live consumer beyond the work test and its own fiscal-year cadence.
