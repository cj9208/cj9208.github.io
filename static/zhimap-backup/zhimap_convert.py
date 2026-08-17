# -*- coding: utf-8 -*-
"""
ZhiMap 导图数据本地转换工具

功能：
  1) 把浏览器导出的 .json 批量转成 FreeMind(.mm) / Markdown / 纯文本
  2) 可选：不依赖浏览器，直接用本脚本 + 登录 cookie 下载全部导图 JSON

用法：
  python zhimap_convert.py convert ./json_dir          # 转换已有 JSON
  python zhimap_convert.py download --cookie "..."      # 直接从网站下载（需 cookie）
  python zhimap_convert.py download --cookie "..." --convert  # 下载并转换
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API = 'https://zhimap.com/restful'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'


def strip_html(s):
    if not s:
        return ''
    t = s.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = t.replace('\u200b', '').replace('\xa0', ' ')
    return re.sub(r'[ \t]+', ' ', t).strip()


def root_title(mm):
    """取根节点标题（比 mindMap.title 更有意义）"""
    tree = (mm.get('trees') or [{}])[0]
    t = strip_html(tree.get('title')) or strip_html(mm.get('title')) or ''
    return t


def safe_name(s, fallback='untitled'):
    s = strip_html(s) if s else ''
    if not s:
        s = fallback
    s = re.sub(r'[\r\n\t]+', ' ', s)
    return re.sub(r'[\\/:*?"<>|\u200b]', '_', s)[:80].strip() or fallback


def xml_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&apos;'))


def node_to_mm(node):
    text = xml_escape(strip_html(node.get('title')))
    note = strip_html(node.get('content'))
    parts = [f'<node TEXT="{text}"']
    if node.get('folded'):
        parts.append(' FOLDED="true"')
    if node.get('link'):
        parts.append(f' LINK="{xml_escape(node["link"])}"')
    parts.append('>')
    if note:
        parts.append(f'<richcontent TYPE="NOTE"><html><body>{xml_escape(note).replace(chr(10), "<br/>")}</body></html></richcontent>')
    for c in node.get('children') or []:
        parts.append(node_to_mm(c))
    parts.append('</node>')
    return ''.join(parts)


def to_freemind(mind_map):
    tree = (mind_map.get('trees') or [{}])[0]
    title = root_title(mind_map) or 'Root'
    root_children = tree.get('children') or []
    body = node_to_mm({'title': title, 'children': root_children})
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<map version="1.0.1">\n{body}\n</map>'


def node_to_md(node, depth=0):
    title = strip_html(node.get('title')) or ''
    note = strip_html(node.get('content'))
    link = node.get('link')
    prefix = '  ' * depth
    lines = [f'{prefix}- {title}']
    if link:
        lines[-1] += f' (link: {link})'
    if note:
        lines.append(f'{prefix}  > {note}')
    for c in node.get('children') or []:
        lines += node_to_md(c, depth + 1)
    return lines


def to_markdown(mind_map):
    tree = (mind_map.get('trees') or [{}])[0]
    lines = [f'# {root_title(mind_map) or "Root"}']
    for c in tree.get('children') or []:
        lines += node_to_md(c, 0)
    return '\n'.join(lines)


def to_text(mind_map):
    md = to_markdown(mind_map)
    return re.sub(r'^#+ ', '', md, flags=re.M)


def convert_one(src_path, out_dir, formats=('mm', 'md', 'txt')):
    j = json.loads(Path(src_path).read_text(encoding='utf-8'))
    mm = j['data']['mindMap'] if isinstance(j.get('data'), dict) and 'mindMap' in j.get('data', {}) else j.get('mindMap')
    if mm is None:
        raise ValueError(f'{src_path.name}: 找不到 mindMap 字段')
    # 从源文件名提取 uuid 后缀（title__uuid.json），保证输出不互相覆盖
    m = re.search(r'__([0-9a-f]{16,})\.json$', src_path.name)
    suffix = '__' + m.group(1) if m else ''
    base = safe_name(root_title(mm) or mm.get('title'), Path(src_path).stem) + suffix
    base = os.path.join(out_dir, base)
    written = []
    if 'mm' in formats:
        p = base + '.mm'
        Path(p).write_text(to_freemind(mm), encoding='utf-8')
        written.append(p)
    if 'md' in formats:
        p = base + '.md'
        Path(p).write_text(to_markdown(mm), encoding='utf-8')
        written.append(p)
    if 'txt' in formats:
        p = base + '.txt'
        Path(p).write_text(to_text(mm), encoding='utf-8')
        written.append(p)
    return written


def convert_dir(json_dir, out_dir, formats):
    json_dir, out_dir = Path(json_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(json_dir.glob('*.json'))
    ok = 0
    for f in files:
        try:
            written = convert_one(f, out_dir, formats)
            print(f'[OK] {f.name} -> {len(written)} 个文件')
            ok += 1
        except Exception as e:
            print(f'[FAIL] {f.name}: {e}')
    print(f'\n完成：{ok}/{len(files)} 张导图已转换，输出目录 {out_dir}')


def http_get(url, cookie, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Cookie': cookie, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        return data if binary else data.decode('utf-8', errors='replace')


def download_all(cookie, out_dir, convert=False):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print('拉取导图列表…')
    raw = http_get(f'{API}/sec/get_uuids?req_num=100000', cookie)
    j = json.loads(raw)
    if j.get('code') != 0:
        print('获取列表失败（cookie 无效或未登录）:', j.get('message'))
        sys.exit(1)
    uuids = j.get('data') or []
    print(f'共 {len(uuids)} 张导图')
    ok = 0
    for i, u in enumerate(uuids, 1):
        try:
            data = http_get(f'{API}/pub/mindmap/load_v?uuid={u}', cookie)
            obj = json.loads(data)
            mm = obj['data']['mindMap']
            base = safe_name(mm.get('title'), u)
            p = out_dir / (base + '__' + u + '.json')
            p.write_text(data, encoding='utf-8')
            if convert:
                convert_one(p, out_dir)
            print(f'[{i}/{len(uuids)}] OK {base}')
            ok += 1
        except Exception as e:
            print(f'[{i}/{len(uuids)}] FAIL {u}: {e}')
    print(f'\n完成：{ok}/{len(uuids)}，输出目录 {out_dir}')


def main():
    ap = argparse.ArgumentParser(description='ZhiMap 导图导出/转换')
    sub = ap.add_subparsers(dest='cmd', required=True)

    c = sub.add_parser('convert', help='转换本地 JSON -> .mm/.md/.txt')
    c.add_argument('json_dir')
    c.add_argument('-o', '--out', default='./converted')
    c.add_argument('-f', '--formats', default='mm,md,txt')

    d = sub.add_parser('download', help='用登录 cookie 直接从网站下载全部导图 JSON')
    d.add_argument('--cookie', required=True, help='登录后浏览器里的完整 Cookie 字符串')
    d.add_argument('-o', '--out', default='./zhimap_json')
    d.add_argument('--convert', action='store_true', help='下载后同时转换')

    args = ap.parse_args()
    if args.cmd == 'convert':
        convert_dir(args.json_dir, args.out, [x.strip() for x in args.formats.split(',')])
    elif args.cmd == 'download':
        download_all(args.cookie, args.out, args.convert)


if __name__ == '__main__':
    main()
