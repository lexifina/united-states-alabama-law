"""Alabama: publish the 14 sections q-645 held (11 with past dates in their bodies, 3 in Title 40) as file-scoped
corrections to the 2026-11-03 snapshot, like the 26 restored before them (append_omissions.py).

Dates, re-read from ALISON's own API on 2026-11-10 (one codesOfAlabama query, includeAllVersions):
- every held section's current row has no effectiveDate, or an official heading date before the snapshot (40-21-83 and
  40-21-103: "(Effective September 1, 2026)"), and a supersessionDate after it (2027-01-01 .. 2029-09-01) or none;
- the dates inside the bodies say when particular rules apply (fees from January 1, 2022, notaries existing on September
  1, 2023, contributions from July 1, 2021, ...), not when the wording took effect. Each is kept, with its context, in
  data/omission-restorations.tsv (body_date_evidence).
So each section is recorded from the snapshot day, 2026-11-03, as every other section of the snapshot is (In-force is
when the record starts, not the section's commencement); the heading date, when there is one, is source_start.

    python -X utf8 publish_held.py <rows.json> <staging folder> --repo <clone, main == origin/main> [--write]
"""
import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'gitlaw_common'))
sys.path.insert(0, str(HERE))
import append_omissions as A  # noqa: E402

HELD = {'32-6-271': 'title-32', '32-6-280': 'title-32', '34-27-33': 'title-34', '34-27-35': 'title-34',
        '36-20-71': 'title-36', '37-15-5': 'title-37', '37-15-6': 'title-37', '37-15-10': 'title-37',
        '37-15-10.1': 'title-37', '40-9-39.4': 'title-40', '40-21-83': 'title-40', '40-21-103': 'title-40',
        '45-37A-51.11': 'title-45', '45-37A-51.190': 'title-45'}
SNAPSHOT, CHECKED = '2026-11-03', '2026-11-10'
BASIS = ('Official heading and API re-read 2026-11-10: the current text carries no commencement date after the snapshot '
         '(40-21-83 and 40-21-103: official heading, effective September 1, 2026) and is superseded only after it; '
         'dates in the body state when particular rules apply, not when this wording took effect (each listed in '
         'data/omission-restorations.tsv); recorded from the snapshot day, as the rest of the snapshot')


def fname(section):
    parts = section.lower().replace('.', '-').split('-')
    return '-'.join(p.zfill(3) if p.isdigit() else (p[:-1].zfill(3) + p[-1] if p[:-1].isdigit() and p[-1].isalpha() else p) for p in parts)


def git(repo, *a):
    return subprocess.run(['git', '-C', str(repo), *a], capture_output=True, check=True).stdout.decode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rows', type=Path)
    ap.add_argument('staging', type=Path)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    repo = a.repo
    head = git(repo, 'rev-parse', 'origin/main').strip()
    raw = a.rows.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = json.loads(raw)['data']['x']['data']
    current = {}
    for row in rows:
        date, _ = A.source_date(row)
        if (date and date > SNAPSHOT) or (row.get('supersessionDate') and row['supersessionDate'] <= CHECKED):
            continue
        if row['displayId'] in current:
            raise SystemExit('ambiguous current row: ' + row['displayId'])
        current[row['displayId']] = (row, date)
    if set(current) != set(HELD):
        raise SystemExit(f'rows: {sorted(set(HELD) ^ set(current))}')
    corpus = json.loads((HERE / 'corpus.json').read_bytes())
    acts = {x['slug']: x for x in corpus['acts']}
    # main's earlier restorations (append_omissions.py, defa706), read back from main itself
    prior = list(csv.DictReader(io.StringIO(git(repo, 'show', head + ':data/omission-restorations.tsv')), delimiter='\t'))
    for r in prior:
        v = acts[r['act']]['versions'][-1]
        v['units'][Path(r['file']).stem] = {'label': 'Section ' + r['section'], 'kind': 'section',
                                            'text': git(repo, 'show', f'{head}:{r["file"]}')}
    records = []
    for sec, slug in HELD.items():
        row, date = current[sec]
        v = acts[slug]['versions'][-1]
        if v['from'] != SNAPSHOT:
            raise SystemExit(slug + ' newest version is not the snapshot')
        f = f'{slug}/{fname(sec)}.md'
        if git(repo, 'ls-tree', head, '--', f).strip():
            raise SystemExit('already on main: ' + f)
        key = Path(f).stem
        if key in v['units']:
            raise SystemExit('unit exists: ' + key)
        v['units'][key] = {'label': 'Section ' + sec, 'kind': 'section', 'text': A.render(row)}
        records.append({'act': slug, 'section': sec, 'file': f, 'in_force': SNAPSHOT, 'source_start': date or '',
                        'recorded_from': SNAPSHOT, 'text_as_of': CHECKED, 'in_force_basis': BASIS,
                        'body_date_evidence': json.dumps(A.body_dates(row), ensure_ascii=False, sort_keys=True),
                        'source_sha256': digest, 'source_url': v['source_url']})
    for slug in {r['act'] for r in prior} | set(HELD.values()):
        v = acts[slug]['versions'][-1]
        v['units'] = dict(sorted(v['units'].items()))
        v['note'] = 'Published snapshot corrected only for omitted sections; file-level source dates are in data/omission-restorations.tsv and the correction trailers.'
    n = len(prior) + len(records)
    corpus['decisions'] = [d for d in corpus['decisions']] + [
        f'{n} sections the first snapshot omitted are restored by labelled, file-scoped corrections (26 on 2026-11-05, 14 on 2026-11-10); existing section wording is unchanged.',
        'Correction ranges start at the published snapshot day, which is also their In-force day: the record starts there, as for every other section, and does not claim the section commenced then. An official heading date (40-21-83, 40-21-103: September 1, 2026) is kept as source_start.',
        'Dates inside a section body (when a fee, licence rule or contribution rate applies) are kept as evidence with their context; none is taken as the date of the section\'s wording.',
        '34-27-35: ALISON\'s current row notes "AMENDED BY ACT 2025-379, EFFECTIVE OCTOBER 1, 2026"; the enrolled act (Section 2) and the API\'s next row both give October 1, 2028, so the current row stays in force until then.']
    a.staging.mkdir(parents=True, exist_ok=True)
    (a.staging / 'corpus.json').write_text(json.dumps(corpus, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    st = a.staging / 'repo'
    if st.exists():
        shutil.rmtree(st)
    for p in ('README.md', 'LICENSE', 'jurisdiction.json', 'corpus.json', 'tools/append_omissions.py'):
        (st / p).parent.mkdir(parents=True, exist_ok=True)
        (st / p).write_bytes(git(repo, 'show', f'{head}:{p}').encode('utf-8'))
    shutil.copy(HERE / 'append_omissions.py', st / 'tools' / 'append_omissions.py')
    shutil.copy(Path(__file__), st / 'tools' / 'publish_held.py')
    (a.staging / 'records.json').write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'prior': len(prior), 'new': len(records), 'files': [r['file'] for r in records]}, indent=1))
    if a.write:
        print(json.dumps(A.append_corrections(a.staging, repo, records, CHECKED, prior=prior,
                                              title='Documentation: Alabama held sections restored, source dates')))


if __name__ == '__main__':
    main()
