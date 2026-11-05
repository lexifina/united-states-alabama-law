"""Restore omitted official sections with file-scoped, append-only corrections.

This Alabama builder uses the shared append module without replacing its functions.
Source commencement dates are separate from the published snapshot's correction range.
"""
import argparse
import copy
import csv
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import append as AP

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3'):
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3'):
            self.parts.append('\n')

def clean(text):
    return re.sub(r'\s+', ' ', html.unescape(text).replace('\xa0', ' ')).strip()

def render(row):
    parser = Text()
    parser.feed(row['content'])
    lines = [clean(line) for line in ''.join(parser.parts).splitlines() if clean(line)]
    return '# ' + clean(row['title']) + '\n' + '\n'.join(lines) + '\n'

def body_dates(row):
    """Keep every full calendar date with context; do not infer whole-section effect."""
    parser = Text()
    parser.feed(row['content'])
    body = clean(' '.join(parser.parts))
    evidence = []
    pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
    for match in re.finditer(pattern, body, re.I):
        day = dt.datetime.strptime(re.sub(r',?\s+', ' ', match[0]), '%B %d %Y').date().isoformat()
        evidence.append({'date': day, 'source_phrase': match[0],
                         'context': body[max(0, match.start()-150):match.end()+150]})
    return evidence

def source_date(row):
    heading = re.search(r'\(Effective ([A-Za-z]+ \d{1,2}, \d{4})\)', row['title'], re.I)
    stated = dt.datetime.strptime(heading[1], '%B %d, %Y').date().isoformat() if heading else None
    field = row.get('effectiveDate')
    if stated and field and stated != field:
        raise ValueError('conflicting commencement dates: ' + row['displayId'])
    return stated or field, ('official heading: ' + heading[0] if heading else
                             'official API effectiveDate' if field else
                             'current commencement unresolved; inspect body date evidence before fallback')

def prepare(source, response, manifest, checked_on):
    corpus = json.loads(Path(source).read_bytes())
    raw = Path(response).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = json.loads(raw)['data']['x']['data']
    current = {}
    for row in rows:
        date, basis = source_date(row)
        if (date and date > checked_on) or (row.get('supersessionDate') and row['supersessionDate'] <= checked_on):
            continue
        if row['displayId'] in current:
            raise ValueError('ambiguous current row: ' + row['displayId'])
        current[row['displayId']] = (row, date, basis)
    acts = {act['slug']: act for act in corpus['acts']}
    records = []
    for item in csv.DictReader(Path(manifest).open(encoding='utf8')):
        row, date, basis = current[item['section']]
        dates = body_dates(row)
        if any(e['date'] <= checked_on for e in dates):
            raise ValueError('hold: body commencement/applicability requires source-based whole-version resolution: ' + row['displayId'])
        if not date:
            basis = ('No date for commencement or past applicability of this current section is stated in the official heading, API or body; '
                     'any future body dates concern prospective amendments, not commencement of this current text; '
                     'the original snapshot date identifies the correction range, not legislative commencement')
        act = acts[item['act']]
        version = act['versions'][-1]
        key = Path(item['missing_published_file']).stem
        if key in version['units']:
            raise ValueError('restoration manifest names existing provision: ' + key)
        version['units'][key] = {'label': 'Section ' + row['displayId'], 'kind': 'section', 'text': render(row)}
        records.append({'act': act['slug'], 'section': row['displayId'], 'file': item['missing_published_file'],
                        'in_force': date or version['from'], 'source_start': date,
                        'recorded_from': version['from'], 'text_as_of': checked_on,
                        'in_force_basis': basis, 'body_date_evidence': json.dumps(dates, ensure_ascii=False, sort_keys=True),
                        'source_sha256': digest, 'source_url': version['source_url']})
    for slug in {record['act'] for record in records}:
        version = acts[slug]['versions'][-1]
        version['units'] = dict(sorted(version['units'].items()))
        version['sha256'] = digest
        version['note'] = 'Published snapshot corrected only for omitted sections; file-level source dates are in data/omission-restorations.tsv and the correction trailers.'
    corpus['country']['default_in_force_rule']['text'] = 'Audit official heading, API and body dates. Hold any section with unresolved past body commencement or applicability dates. Future amendment dates do not commence current wording. Undated correction records retain the original snapshot range and separately identify the observation date.'
    corpus['decisions'] = [f'{len(records)} previously omitted official sections are restored by labelled, file-scoped corrections; existing section wording is unchanged.',
        'Correction ranges start at the original published snapshot, independently of a provision commencement date.',
        'Sections 40-21-83 and 40-21-103 explicitly commence September 1, 2026 in their official headings; null API fields do not override those dates.',
        'Future supersession dates retain current wording until expiry; future effective dates exclude future wording.',
        'Eleven sections with unresolved past body dates, including six reviewer findings, are held. No section-level date is inferred from a partial applicability clause. Title 40 remains held.',
        'Seventy-two inherited source mismatches remain outside this restoration. The corpus is not represented as completely source-verified.']
    corpus['ai_use'] = ['A model implemented extraction, validation and documentation. Legal wording is extracted from official HTML; no model altered law words.']
    return corpus, records

def append_corrections(folder, repo, records, docs_date):
    corpus, raw = AP.B.load(folder)
    errors = AP.B.validate(corpus)
    if errors:
        raise ValueError(errors)
    head = AP.git(repo, 'rev-parse', 'main').strip()
    if AP.git(repo, 'rev-parse', 'origin/main').strip() != head:
        raise ValueError('scratch must start at published main')
    if AP.git(repo, 'status', '--porcelain').strip():
        raise ValueError('scratch must be clean')
    groups = {}
    acts = {act['slug']: act for act in corpus['acts']}
    for record in records:
        groups.setdefault((record['act'], record['in_force'], record['recorded_from']), []).append(record)
    planned = []
    for (slug, day, recorded), items in sorted(groups.items(), key=lambda pair: (pair[0][1], pair[0][0])):
        act = acts[slug]
        supersedes = AP.K.state_on(AP.K.all_commits_by_act(repo, 'main', [slug])[slug], recorded)
        if not supersedes:
            raise ValueError('no published snapshot to correct: ' + slug)
        files = {item['file']: act['versions'][-1]['units'][Path(item['file']).stem]['text'] for item in items}
        if any(AP.git(repo, 'ls-tree', head, '--', file).strip() for file in files):
            raise ValueError('correction must add only omitted paths')
        reason = 'Restore official current sections omitted from the published snapshot; preserve all existing section wording'
        basis = items[0]['in_force_basis']
        if any(item['in_force_basis'] != basis for item in items):
            raise ValueError('inconsistent source-date basis within correction')
        trailers = ['Kind: correction', f'In-force: {day}', f'Corrects: {slug} {recorded}..',
                    f'Supersedes: {supersedes}', f'Reason: {reason}', f'Act-path: {slug}',
                    f'Text-as-of: {docs_date}', f'In-force-basis: {basis}', f'Source: {act["url"]}',
                    f'Text-source: {items[0]["source_url"]}', f'Source-sha256: {items[0]["source_sha256"]}']
        trailers += [f'Files: {file}' for file in sorted(files)]
        AP.B.check_trailers(trailers)
        message = f'Correction: {act["short"]}, restore {len(files)} omitted sections\n\n' + reason + '.\n'
        message += 'Source commencement and the published snapshot correction range are recorded separately.\n\n'
        planned.append((day, slug, files, message + '\n'.join(trailers) + '\n'))
    ct, tz = AP.git(repo, 'log', '-1', '--format=%ct %ci', head).split()[0::3]
    writer = AP.Appender(repo, head, int(ct), tz)
    identity = ('Lexifina', 'united-states-alabama-law@lexifina.com')
    clock = AP.B.Clock(corpus['country']['tz'])
    log = AP.published_log(repo)
    for day, slug, files, message in planned:
        writer.commit(identity, clock.stamp(day), identity, message, files)
        log.append({'day': day, 'kind': 'correction', 'law': None, 'acts': [slug], 'units': len(files), 'branch': 'main', 'clamped': False})
    corpus['_docs_date'] = docs_date
    docs = AP.B.docs_files(corpus, folder, raw, log, {tag: 0 for tag in AP.git(repo, 'tag').splitlines()}, docs_date)
    docs['tools/append.py'] = Path(AP.__file__).read_text(encoding='utf8').replace('\r\n', '\n')
    fields = list(records[0])
    import io
    stream = io.StringIO()
    table = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
    table.writeheader(); table.writerows(records)
    docs['data/omission-restorations.tsv'] = stream.getvalue()
    author_stamp = clock.stamp(docs_date).split()
    import time
    author_stamp[0] = str(min(int(author_stamp[0]), int(time.time())))
    writer.commit(identity, ' '.join(author_stamp), identity,
                  f'Documentation: Alabama omitted-section corrections and source dates\n\nKind: documentation\nSource: https://alison.legislature.state.al.us/code-of-alabama\n', docs)
    writer.finish()
    AP.git(repo, 'checkout', '-q', '-f', 'main')
    return {'base': head, 'head': AP.git(repo, 'rev-parse', 'main').strip(), 'corrections': len(planned), 'sections': len(records), 'tags_added': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--docs-date', required=True)
    args = parser.parse_args()
    print(json.dumps(append_corrections(args.folder, args.repo, json.loads(args.records.read_bytes()), args.docs_date)))
