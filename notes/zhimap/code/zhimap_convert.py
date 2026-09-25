# -*- coding: utf-8 -*-
"""
ZhiMap 导图数据本地转换工具

功能：
  1) 把浏览器导出的 .json 批量转成 FreeMind(.mm) / Markdown / 纯文本
     - 所有分支完整展开（存档里折叠的节点也会输出）
     - 节点内嵌图片输出为 Markdown 图片，公式输出为 $tex$
  2) 把节点里引用的 /res/ 图片抓到本地 assets 目录（公开路径，无需登录）
  3) 可选：不依赖浏览器，直接用本脚本 + 登录 cookie 下载全部导图 JSON

用法：
  python zhimap_convert.py convert ./json_dir                # 转换已有 JSON
  python zhimap_convert.py convert ./json_dir --fetch-assets  # 先抓图再转换
  python zhimap_convert.py assets ./json_dir -o ./assets      # 只抓内嵌图片
  python zhimap_convert.py download --cookie "..."             # 直接从网站下载（需 cookie）
  python zhimap_convert.py download --cookie "..." --convert   # 下载并转换
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
SITE = 'https://zhimap.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'

KATEX_OPEN = re.compile(r'<span class="katex[" ]')
ANNOTATION = re.compile(r'<annotation encoding="application/x-tex">(.*?)</annotation>', re.S)
IMG_TAG = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', re.I)
_IMG_MARK = '\x01{}\x02'


def strip_html(s):
    if not s:
        return ''
    t = s.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = t.replace('\u200b', '').replace('\xa0', ' ')
    return re.sub(r'[ \t]+', ' ', t).strip()


def _span_end(s, start):
    """Return index just past the </span> matching the opening tag at `start`."""
    depth = 0
    i = start
    while True:
        m = re.compile(r'</?span\b').search(s, i)
        if not m:
            return len(s)
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                close = s.find('>', m.end())
                return len(s) if close < 0 else close + 1
        else:
            depth += 1
        i = m.end()


def _katex_to_tex(s, fmt=' ${tex}$ '):
    """Replace each rendered KaTeX span with its source, formatted by `fmt`."""
    out, i = [], 0
    while True:
        m = KATEX_OPEN.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        end = _span_end(s, m.start())
        tex = ANNOTATION.search(s[m.start():end])
        if tex:
            out.append(fmt.replace('{tex}', html.unescape(tex.group(1)).strip()))
        i = end
    return ''.join(out)


def render_node(s):
    """ZhiMap node HTML -> (plain text with $math$, [image src, ...])."""
    if not s:
        return '', []
    images = [m.group(1) for m in IMG_TAG.finditer(s)]
    t = IMG_TAG.sub(lambda m: _IMG_MARK.format(m.group(1)), s)
    t = _katex_to_tex(t)
    t = re.sub(r'\x01[^\x02]*\x02', '', t)
    t = t.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t).replace('\u200b', '').replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = '\n'.join(line.strip() for line in t.split('\n'))
    t = re.sub(r'\n{2,}', '\n', t).strip()
    return t, images


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
    text = xml_escape(render_node(node.get('title'))[0])
    note = render_node(node.get('content'))[0]
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


def _asset_ref(src, assets_dir):
    if not assets_dir:
        return src if src.startswith('http') else SITE + src
    return f'{assets_dir.rstrip("/")}/{Path(src.split("?")[0]).name}'


def node_to_md(node, depth=0, assets_dir='assets'):
    prefix = '  ' * depth
    title, images = render_node(node.get('title'))
    note, note_images = render_node(node.get('content'))
    link = node.get('link')
    segs = ([title.replace('\n', ' ').strip()] if title.strip() else [])
    segs += [f'![{Path(ref).name}]({ref})' for ref in (_asset_ref(s, assets_dir) for s in images)]
    line = f'{prefix}- ' + ' '.join(segs)
    if link:
        line += f' (link: {link})'
    lines = [line]
    for src in note_images:
        ref = _asset_ref(src, assets_dir)
        lines.append(f'{prefix}  ![{Path(ref).name}]({ref})')
    if note:
        for seg in note.split('\n'):
            lines.append(f'{prefix}  > {seg}')
    for c in node.get('children') or []:
        lines += node_to_md(c, depth + 1, assets_dir)
    return lines


def _walk_nodes(mind_map):
    def rec(n):
        yield n
        for c in n.get('children') or []:
            yield from rec(c)
    for t in mind_map.get('trees') or []:
        yield from rec(t)


def collect_image_srcs(mind_map):
    srcs = []
    for n in _walk_nodes(mind_map):
        srcs += render_node(n.get('title'))[1] + render_node(n.get('content'))[1]
    return srcs


def to_markdown(mind_map, assets_dir='assets'):
    tree = (mind_map.get('trees') or [{}])[0]
    lines = [f'# {root_title(mind_map) or "Root"}']
    for c in tree.get('children') or []:
        lines += node_to_md(c, 0, assets_dir)
    return '\n'.join(lines)


def convert_one(src_path, out_dir, formats=('md',), assets_dir='assets'):
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
        Path(p).write_text(to_markdown(mm, assets_dir), encoding='utf-8')
        written.append(p)
    return written


def gather_srcs(json_dir):
    srcs = set()
    for f in sorted(Path(json_dir).glob('*.json')):
        try:
            j = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            print(f'[FAIL] {f.name}: {e}')
            continue
        data = j.get('data') or {}
        mm = data.get('mindMap') if isinstance(data, dict) else None
        if mm:
            srcs.update(collect_image_srcs(mm))
    return sorted(srcs)


def fetch_assets(json_dir, assets_out):
    """Download every image embedded in node HTML. Public /res/ paths need no login."""
    assets_out = Path(assets_out)
    assets_out.mkdir(parents=True, exist_ok=True)
    srcs = gather_srcs(json_dir)
    ok = skip = 0
    failed = []
    for i, src in enumerate(srcs, 1):
        url = src if src.startswith('http') else SITE + src
        dest = assets_out / Path(src.split('?')[0]).name
        if dest.exists() and dest.stat().st_size > 0:
            skip += 1
            continue
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': SITE + '/'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            is_image = data[:4] == b'\x89PNG' or data[:3] == b'\xff\xd8\xff' or data[:4] in (b'GIF8', b'RIFF')
            if not is_image:
                print(f'[WARN] {url} 返回内容不是图片（{len(data)} 字节）')
            dest.write_bytes(data)
            ok += 1
            print(f'[{i}/{len(srcs)}] {dest.name} ({len(data)} bytes)')
        except Exception as e:
            failed.append((url, str(e)))
            print(f'[{i}/{len(srcs)}] FAIL {url}: {e}')
    print(f'\n图片：新下载 {ok}，已存在 {skip}，失败 {len(failed)}，共 {len(srcs)} 张引用')
    return len(srcs), ok, skip, failed


def convert_dir(json_dir, out_dir, formats, assets_dir='assets'):
    json_dir, out_dir = Path(json_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(json_dir.glob('*.json'))
    ok = 0
    for f in files:
        try:
            written = convert_one(f, out_dir, formats, assets_dir)
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

    c = sub.add_parser('convert', help='转换本地 JSON -> .md（-f mm 可另外出 FreeMind）')
    c.add_argument('json_dir')
    c.add_argument('-o', '--out', default='./converted')
    c.add_argument('-f', '--formats', default='md')
    c.add_argument('--assets-dir', default='assets',
                   help='Markdown 里图片的路径前缀（相对输出的 .md 所在目录）')
    c.add_argument('--remote', action='store_true',
                   help='不本地化，Markdown 里直接引用 zhimap.com 原图 URL')
    c.add_argument('--fetch-assets', action='store_true',
                   help='转换前先把节点内嵌图片抓到 --assets-dir 指定目录')

    a = sub.add_parser('assets', help='只下载 JSON 里内嵌的图片到本地 assets 目录')
    a.add_argument('json_dir')
    a.add_argument('-o', '--out', default='./assets')

    d = sub.add_parser('download', help='用登录 cookie 直接从网站下载全部导图 JSON')
    d.add_argument('--cookie', required=True, help='登录后浏览器里的完整 Cookie 字符串')
    d.add_argument('-o', '--out', default='./zhimap_json')
    d.add_argument('--convert', action='store_true', help='下载后同时转换')

    args = ap.parse_args()
    if args.cmd == 'convert':
        assets_dir = '' if args.remote else args.assets_dir
        if getattr(args, 'fetch_assets', False):
            fetch_assets(args.json_dir, Path(args.out) / args.assets_dir)
        convert_dir(args.json_dir, args.out, [x.strip() for x in args.formats.split(',')], assets_dir)
    elif args.cmd == 'assets':
        fetch_assets(args.json_dir, args.out)
    elif args.cmd == 'download':
        download_all(args.cookie, args.out, args.convert)


if __name__ == '__main__':
    main()
