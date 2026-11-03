# How this repository was made (United States (Alabama))

This file is written by the build on 2026-11-03, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Alabama Legislature, Code of Alabama 1975 and Constitution of Alabama | <https://alison.legislature.state.al.us/code-of-alabama> | 2026-10-30 | Public statute text |
| Alabama Legislature (ALISON) | <https://alison.legislature.state.al.us/code-of-alabama> | 2026-11-03 | Public statute text |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of Alabama (2022 recompilation) | 1 | 2026-10-30 to 2026-10-30 |
| `title-13a` | Code of Alabama 1975, Title 13A Criminal Code | 1 | 2026-10-30 to 2026-10-30 |
| `title-10a` | Code of Alabama 1975, Title 10A Alabama Business and Nonprofit Entities Code | 1 | 2026-10-30 to 2026-10-30 |
| `title-35` | Code of Alabama 1975, Title 35 Property | 1 | 2026-10-30 to 2026-10-30 |
| `title-1` | Code of Alabama 1975, Title 1 General Provisions | 1 | 2026-11-03 to 2026-11-03 |
| `title-2` | Code of Alabama 1975, Title 2 Agriculture | 1 | 2026-11-03 to 2026-11-03 |
| `title-3` | Code of Alabama 1975, Title 3 Animals | 1 | 2026-11-03 to 2026-11-03 |
| `title-4` | Code of Alabama 1975, Title 4 Aviation | 1 | 2026-11-03 to 2026-11-03 |
| `title-5` | Code of Alabama 1975, Title 5 Banks and Financial Institutions | 1 | 2026-11-03 to 2026-11-03 |
| `title-6` | Code of Alabama 1975, Title 6 Civil Practice | 1 | 2026-11-03 to 2026-11-03 |
| `title-7` | Code of Alabama 1975, Title 7 Commercial Code | 1 | 2026-11-03 to 2026-11-03 |
| `title-8` | Code of Alabama 1975, Title 8 Commercial Law and Consumer Protection | 1 | 2026-11-03 to 2026-11-03 |
| `title-9` | Code of Alabama 1975, Title 9 Conservation and Natural Resources | 1 | 2026-11-03 to 2026-11-03 |
| `title-10` | Code of Alabama 1975, Title 10 Corporations, Partnerships, and Associations | 1 | 2026-11-03 to 2026-11-03 |
| `title-11` | Code of Alabama 1975, Title 11 Counties and Municipal Corporations | 1 | 2026-11-03 to 2026-11-03 |
| `title-12` | Code of Alabama 1975, Title 12 Courts | 1 | 2026-11-03 to 2026-11-03 |
| `title-14` | Code of Alabama 1975, Title 14 Criminal Correctional and Detention Facilities | 1 | 2026-11-03 to 2026-11-03 |
| `title-15` | Code of Alabama 1975, Title 15 Criminal Procedure | 1 | 2026-11-03 to 2026-11-03 |
| `title-16` | Code of Alabama 1975, Title 16 Education | 1 | 2026-11-03 to 2026-11-03 |
| `title-17` | Code of Alabama 1975, Title 17 Elections | 1 | 2026-11-03 to 2026-11-03 |
| `title-18` | Code of Alabama 1975, Title 18 Eminent Domain | 1 | 2026-11-03 to 2026-11-03 |
| `title-19` | Code of Alabama 1975, Title 19 Fiduciaries and Trusts | 1 | 2026-11-03 to 2026-11-03 |

The build made 22 commits:

| Commits | Kind |
| ---: | --- |
| 22 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-11-03.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 22 laws in the record.
- 22 tags.

## Dates

Each commit is dated at noon (America/Chicago) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: No dated history is published: each text is the oldest version available, dated from the retrieval day. https://alison.legislature.state.al.us/code-of-alabama

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `927f60d0209f050ad443d095b6635bebb764436d096ed0f792aef91a6be08968` (29684898 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- English only. First build: the Constitution and Code titles 13A (Criminal Code), 10A (Business and Nonprofit Entities Code) and 35 (Property).
- Every text has one version, "oldest version available", dated from the retrieval day and credited to the publisher; the site publishes no dated point-in-time history for these titles.
- Sections that carry an effective or supersession date (future or superseded wording) are left out of this first build.
- Source histories, notes and annotations are not included; only statute text.
- Wave 3 (2026-11-03): every other Code of Alabama title in this part is added, one act per title, parsed as in the first build (rows carrying an effective or supersession date are left out: 28).
- Each new title is dated by the retrieval day (2026-11-03) and credited to the publisher as the oldest version available, so its current wording is never dated before its latest amendment took effect.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none (scripts only; no model wrote or altered legal text)
