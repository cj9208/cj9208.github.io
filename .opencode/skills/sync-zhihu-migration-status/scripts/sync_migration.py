import json, os, re, sys, unicodedata, datetime, argparse
from difflib import SequenceMatcher

def out(x):
    sys.stdout.buffer.write((x + '\n').encode('utf-8', 'replace'))
    sys.stdout.buffer.flush()

def norm(s):
    s = (s or '').strip().lower()
    oc = []
    for ch in s:
        if unicodedata.category(ch)[0] in ('P', 'S', 'Z') or ch in ' \t\n\r':
            continue
        oc.append(ch)
    return ''.join(oc)

def norm_title(s):
    return norm(s.replace('\\"', '').replace("\\'", ''))

def read_utf8(p):
    with open(p, 'r', encoding='utf-8-sig') as fh:
        return fh.read()

def write_utf8(p, text, has_bom=False):
    enc = 'utf-8-sig' if has_bom else 'utf-8'
    with open(p, 'w', encoding=enc, newline='\n') as fh:
        fh.write(text)


def parse_record(record_path):
    """Parse the record markdown table into rows.

    Returns (lines, rows, header_idx) where rows is a list of dicts:
      idx   - 1-based 序号 as in file
      title - title text with ** stripped
      bold  - whether title was wrapped in **...**
      url   - article url
      created, updated - timestamp strings
      status - 已迁移 / 未迁移
      line_idx - line index in lines
    """
    lines = read_utf8(record_path).split('\n')
    rows = []
    # table lines start with '|'
    for li, line in enumerate(lines):
        s = line.strip()
        if not (s.startswith('|') and s.endswith('|')):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 6:
            continue
        # skip header & separator: header row contains 序号 and 迁移状态; separator row contains ---
        if cells[0] == '序号' or set(cells[0]) <= set('-| '):
            continue
        title_cell = cells[1]
        bold = title_cell.startswith('**') and title_cell.endswith('**')
        title = title_cell[2:-2] if bold else title_cell
        rows.append({
            'line_idx': li,
            'seq': cells[0],
            'title': title,
            'bold': bold,
            'url': cells[2],
            'created': cells[3],
            'updated': cells[4],
            'status': cells[5],
        })
    return lines, rows


def fmt_created(created_str):
    """Convert '2017-09-24 12:39:29 +08:00' -> '2017-09-24T12:39:29+08:00'."""
    m = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\+08:00)$', created_str.strip())
    if not m:
        return None
    return '%sT%s%s' % (m.group(1), m.group(2), m.group(3))


def scan_local(base):
    records = []
    for root, dirs, files in os.walk(base):
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            p = os.path.join(root, f)
            if f in ('_index.md', 'progress.md'):
                continue
            text = read_utf8(p)
            fm = {}
            m = re.match(r'\A---\s*\n(.*?)\n---', text, re.S)
            if m:
                fm = dict(re.findall(r'^([\w-]+):\s*(.+)$', m.group(1), re.M))
            records.append({
                'path': os.path.relpath(p, os.getcwd()).replace('\\', '/'),
                'title': fm.get('title', ''),
                'date': fm.get('date', ''),
            })
    return records


def build_plan(local_records, rows):
    """Match local articles to 未迁移 record rows; return plan entries."""
    # index record rows by normalized title
    by_nt = {}
    for r in rows:
        by_nt.setdefault(norm_title(r['title']), []).append(r)

    plan = []
    for lr in local_records:
        lt = norm_title(lr.get('title', ''))
        if not lt:
            continue
        cands = by_nt.get(lt, [])
        how = 'exact'
        if len(cands) != 1:
            cands = []
            for nt, rs in by_nt.items():
                ratio = SequenceMatcher(None, lt, nt).ratio()
                if ratio >= 0.92:
                    cands.extend(rs)
            how = 'fuzzy'
        if len(cands) != 1:
            continue
        row = cands[0]
        plan.append({
            'path': lr['path'],
            'local_title': lr.get('title', ''),
            'local_date': lr.get('date', ''),
            'row_line': row['line_idx'],
            'zh_title': row['title'],
            'created': row['created'],
            'new_date': fmt_created(row['created']),
            'status': row['status'],
            'how': how,
        })
    return plan


def apply_plan(plan, record_path, lines, dry_run=False):
    """Update local front-matter date and record row status."""
    LASTMOD = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:%S+08:00')
    # group plan by record row line so we only touch each row once
    row_updates = {}
    for item in plan:
        if item['status'] != '未迁移':
            continue
        if item['new_date'] is None:
            continue
        row_updates.setdefault(item['row_line'], []).append(item)

    changed = []
    for line_idx, items in row_updates.items():
        # pick the row's canonical created (all items share same row)
        created = items[0]['created']
        new_date = items[0]['new_date']
        if not dry_run:
            # rebuild row line
            old_line = lines[line_idx]
            cells = [c.strip() for c in old_line.strip('|').split('|')]
            # cells[1] is title cell (may be bold); cells[5] is status
            cells[1] = cells[1][2:-2] if cells[1].startswith('**') else cells[1]
            cells[5] = '已迁移'
            lines[line_idx] = '| ' + ' | '.join(cells) + ' |'
        changed.append((line_idx, new_date))
        for it in items:
            out('  row#%s %s : %s -> %s' % (line_idx, it['zh_title'], it['created'], new_date))

    # update local front matter
    for item in plan:
        if item['status'] != '未迁移' or item['new_date'] is None:
            continue
        p = item['path']
        full = os.path.join(os.getcwd(), p)
        if not os.path.exists(full):
            out('  MISSING %s' % p)
            continue
        text = read_utf8(full)
        has_bom = open(full, 'rb').read(3) == b'\xef\xbb\xbf'
        new_text = re.sub(r'^(date:)\s*.*$', 'date: %s' % item['new_date'], text, count=1, flags=re.M)
        new_text = re.sub(r'^(lastmod:)\s*.*$', 'lastmod: %s' % LASTMOD, new_text, count=1, flags=re.M)
        if new_text == text:
            out('  NO CHANGE %s' % p)
            continue
        if not dry_run:
            write_utf8(full, new_text, has_bom)
        out('  local %s : date -> %s (lastmod -> %s)' % (p, item['new_date'], LASTMOD))

    if not dry_run:
        write_utf8(record_path, '\n'.join(lines))
    return len(row_updates)


def main():
    ap = argparse.ArgumentParser(description='Sync Zhihu migration status')
    ap.add_argument('--record', default='zhihu-column-c_132070558-articles.md',
                    help='path to record markdown (default: repo root)')
    ap.add_argument('--base', default='content/blog',
                    help='base dir to scan local articles')
    ap.add_argument('--apply', action='store_true',
                    help='actually write changes; default is dry-run report')
    args = ap.parse_args()

    record_path = os.path.join(os.getcwd(), args.record)
    lines, rows = parse_record(record_path)
    unmigrated = [r for r in rows if r['status'] == '未迁移']
    out('record rows=%d 未迁移=%d 已迁移=%d' % (
        len(rows), len(unmigrated), len(rows) - len(unmigrated)))

    local_records = scan_local(args.base)
    out('local articles=%d' % len(local_records))

    plan = build_plan(local_records, rows)
    matched_unmigrated = [p for p in plan if p['status'] == '未迁移']
    out('matched to 未迁移 rows: %d' % len(matched_unmigrated))
    if not matched_unmigrated:
        out('No newly-migrated articles matched. Nothing to do.')
        return
    out('--- plan (dry-run) ---' if not args.apply else '--- applying ---')
    n = apply_plan(matched_unmigrated, record_path, lines, dry_run=not args.apply)
    out('rows to update: %d' % n)
    if not args.apply:
        out('Run with --apply to write changes.')


if __name__ == '__main__':
    main()
