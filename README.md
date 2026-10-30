# United States (Alabama): law history in git

A first build of Alabama law as git: one file per section, with the text published by the [Alabama Legislature](https://alison.legislature.state.al.us/code-of-alabama). It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `united-states/alabama/`. Language: English.

**What is in it now**

| Folder | Law | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of Alabama (2022 recompilation, as amended) | 1 | Oldest version available (retrieved 2026-10-30) |
| `title-13a/` | Code of Alabama 1975, Title 13A, Criminal Code | 1 | Oldest version available (retrieved 2026-10-30) |
| `title-10a/` | Code of Alabama 1975, Title 10A, Alabama Business and Nonprofit Entities Code | 1 | Oldest version available (retrieved 2026-10-30) |
| `title-35/` | Code of Alabama 1975, Title 35, Property | 1 | Oldest version available (retrieved 2026-10-30) |

## What it does not show

- **Past versions.** The Legislature site publishes the current Code; none of these sections carries an earlier dated version. Each text therefore has one commit, "oldest version available", credited to the publisher and dated by the retrieval day.
- **Other titles.** The rest of the Code of Alabama is not yet included.
- **Notes.** Source histories, catchline notes and annotations are not law text and are not in the files.

## How it is checked

Every version names its source and the sha256 of the data it was read from. Each version is read back from git and must match `corpus.json` (`tools/check_repo.py`); the results are in `REPRODUCE.md`.

## Sources

| Source | Kind | Past versions | Licence |
| --- | --- | --- | --- |
| [Alabama Legislature](https://alison.legislature.state.al.us/code-of-alabama) | Official legislature site | no | Statute text is not copyrightable (Georgia v. Public.Resource.Org, 2020) |

## Licence

See `LICENSE`. This repository is not legal advice and not an official publication.
