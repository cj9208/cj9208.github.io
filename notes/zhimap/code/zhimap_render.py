# -*- coding: utf-8 -*-
"""
ZhiMap 导图 -> 完全展开的高清整图 PNG

为什么不用官方导出：
  /restful/sec/export?type=png 按存档里的折叠状态渲染（折叠分支直接变成 "..."），
  且画布锁死 1600x1130，scale/width/dpi 参数一律无效。
  本脚本改为读本地 JSON，自己排版成 HTML（所有分支展开）再用 headless Chrome 截图。

流程：
  JSON -> 自包含 HTML（等图片/字体/KaTeX 就绪 -> 浏览器内量尺寸 -> tidy-tree 排版 -> SVG 连线）
       -> Chrome --dump-dom 读出画布尺寸（决定倍率）
       -> Chrome --screenshot 出图
       -> PIL 按背景色裁掉多余边、补回留白

用法：
  python zhimap_render.py <json目录> -o <png目录>
  python zhimap_render.py <json目录> -o <png目录> --only RAG --keep-html
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from zhimap_convert import SITE, IMG_TAG, _katex_to_tex, root_title, safe_name

CHROME_CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
]

H_GAP = 46          # 父子层间距
V_GAP = 16          # 兄弟间距
PAD = 40            # 画布留白
MAX_TEXT_W = 340    # 单个节点标签最大宽度
MAX_IMG_W = 480     # 节点内嵌图片最大显示宽度

TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<style>
  html, body { margin: 0; padding: 0; background: __BG__; }
  body { position: relative; font-family: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif; }
  .node { position: absolute; box-sizing: border-box; font-size: 14px; line-height: 1.45; color: #282828;
          word-break: break-word; }
  .node p { margin: 0; }
  .node img { display: block; margin: 3px 0; max-width: __MAXIMG__px; height: auto; }
  .node.d0 { font-size: 17px; font-weight: 600; }
  .node.d1 { font-size: 15px; font-weight: 600; }
  .node.root { background: #ececec; border-radius: 6px; padding: 10px 14px; font-size: 19px; font-weight: 700; }
  .note { color: #888; font-size: 12px; font-weight: 400; margin-top: 2px; }
  .lk { color: #3a8ddf; font-size: 11px; font-weight: 400; }
  svg.links { position: absolute; left: 0; top: 0; pointer-events: none; }
  #measure { position: absolute; left: 0; top: 0; width: 20000px; visibility: hidden; }
  #measure .node { position: static; display: inline-block; clear: both; }
</style>
</head>
<body>
<div id="measure"></div>
<script>
var DATA = __DATA__;
var CFG = {HGAP: __HGAP__, VGAP: __VGAP__, PAD: __PAD__, MAXW: __MAXW__};
var root = DATA.root;

function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d; }
function htmlOf(n) {
  var s = n.t || '';
  if (n.k) s += '<div class="note">备注: ' + n.k + '</div>';
  if (n.l) s += '<div class="lk">' + n.l + '</div>';
  return s;
}
function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

// 等图片真的解码完、字体和 KaTeX 就位——否则量出来的宽高是错的
function waitReady() {
  var deadline = Date.now() + 15000;
  function pending() {
    return Array.prototype.slice.call(document.images)
      .some(function (i) { return !i.complete; });
  }
  return (function poll() {
    if (pending() && Date.now() < deadline) return sleep(150).then(poll);
    return sleep(200);
  })().then(function () {
    return document.fonts && document.fonts.ready ? document.fonts.ready.catch(function () {}) : null;
  });
}

function typeset(e) {
  e.querySelectorAll('span.km').forEach(function (sp) {
    var tex = sp.textContent;
    if (window.katex) {
      try { sp.outerHTML = katex.renderToString(tex); return; } catch (err) {}
    }
    sp.outerHTML = '<span class="kmfail">' + tex.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span>';
  });
}

// 1) 测量：先把所有标签（含已排版的公式）建进隐藏容器，等图片和字体就位，再读宽高
function buildBoxes() {
  var measure = document.getElementById('measure');
  (function sizeAll(n, level) {
    n.level = level;
    var box = el('<div class="' + (level < 0 ? 'node root' : 'node d' + level) +
                  '" style="max-width:' + CFG.MAXW + 'px">' + htmlOf(n) + '</div>').firstChild;
    measure.appendChild(box);
    typeset(box);
    n.html = box.innerHTML;
    n.bad = box.querySelectorAll('span.km,span.kmfail').length;
    n.box = box;
    (n.c || []).forEach(function (c) { sizeAll(c, level + 1); });
  })(root, -1);
}
function readSizes() {
  (function walk(n) {
    n.w = n.box.offsetWidth;
    n.h = n.box.offsetHeight;
    n.box = null;
    (n.c || []).forEach(walk);
  })(root);
  document.getElementById('measure').innerHTML = '';
}

// 2) 排版：tidy tree。ax 是"靠近父节点的那条边"——右侧分支取节点左边，左侧分支取右边
function subH(n) {
  var kids = n.c || [];
  if (!kids.length) { n.sh = n.h; n.stack = 0; return n.sh; }
  var total = 0;
  kids.forEach(function (c, i) { total += subH(c) + (i ? CFG.VGAP : 0); });
  n.stack = total;
  n.sh = Math.max(n.h, total);
  return n.sh;
}
function place(n, top, ax, sign) {
  n.y = top + (n.sh - n.h) / 2;
  n.x = sign > 0 ? ax : ax - n.w;
  var y = top + (n.sh - n.stack) / 2;
  (n.c || []).forEach(function (c) {
    place(c, y, sign > 0 ? ax + n.w + CFG.HGAP : ax - n.w - CFG.HGAP, sign);
    y += c.sh + CFG.VGAP;
  });
}

function layout() {
  subH(root);
  var sides = {right: [], left: []};
  (root.c || []).forEach(function (c) { sides[c.side === 'left' ? 'left' : 'right'].push(c); });
  Object.keys(sides).forEach(function (k) {
    var total = 0;
    sides[k].forEach(function (c, i) { total += c.sh + (i ? CFG.VGAP : 0); });
    sides[k].stack = total;
  });
  root.stack = Math.max(sides.right.stack, sides.left.stack);
  root.sh = Math.max(root.h, root.stack);
  root.x = -root.w / 2;
  root.y = (root.sh - root.h) / 2;
  [[sides.right, 1], [sides.left, -1]].forEach(function (pair) {
    var arr = pair[0], sign = pair[1];
    var edge = sign > 0 ? root.x + root.w : root.x;
    var y = (root.sh - arr.stack) / 2;
    arr.forEach(function (c) { place(c, y, edge, sign); y += c.sh + CFG.VGAP; });
  });

  var all = [];
  (function collect(n) { all.push(n); (n.c || []).forEach(collect); })(root);
  var bb = [Infinity, Infinity, -Infinity, -Infinity];
  all.forEach(function (n) {
    bb[0] = Math.min(bb[0], n.x); bb[1] = Math.min(bb[1], n.y);
    bb[2] = Math.max(bb[2], n.x + n.w); bb[3] = Math.max(bb[3], n.y + n.h);
  });
  var ox = CFG.PAD - bb[0], oy = CFG.PAD - bb[1];
  var W = Math.ceil(bb[2] - bb[0] + CFG.PAD * 2), H = Math.ceil(bb[3] - bb[1] + CFG.PAD * 2);

  var paths = [];
  (function draw(n, color) {
    (n.c || []).forEach(function (c) {
      var toRight = c.x >= n.x;
      var a = toRight ? [n.x + n.w, n.y + n.h / 2] : [n.x, n.y + n.h / 2];
      var b = toRight ? [c.x, c.y + c.h / 2] : [c.x + c.w, c.y + c.h / 2];
      var mx = (a[0] + b[0]) / 2;
      paths.push('<path d="M' + (a[0] + ox) + ',' + (a[1] + oy) +
                 ' C' + mx + ',' + (a[1] + oy) + ' ' + mx + ',' + (b[1] + oy) +
                 ' ' + (b[0] + ox) + ',' + (b[1] + oy) +
                 '" fill="none" stroke="' + color + '" stroke-width="1.6"/>');
      draw(c, color);
    });
  })(root, '#c0c0c0');

  var bad = 0;
  all.forEach(function (n) {
    var h = n.html || htmlOf(n);
    bad += n.bad || 0;
    n.html = null;
    var d = el(h);
    d.className = n === root ? 'node root' : 'node d' + n.level;
    d.style.left = Math.round(n.x + ox) + 'px';
    d.style.top = Math.round(n.y + oy) + 'px';
    d.style.maxWidth = CFG.MAXW + 'px';
    document.body.appendChild(d);
  });
  var ov = 0;
  for (var i = 0; i < all.length; i++) {
    for (var j = i + 1; j < all.length; j++) {
      var a = all[i], b = all[j];
      if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) ov++;
    }
  }
  document.body.insertAdjacentHTML('afterbegin',
    '<svg class="links" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">' +
    paths.join('') + '</svg>');
  document.body.style.width = W + 'px';
  document.body.style.height = H + 'px';
  document.body.setAttribute('data-canvas', W + ',' + H);
  document.body.setAttribute('data-badmath', String(bad));
  document.body.setAttribute('data-overlaps', String(ov));
  document.body.setAttribute('data-overflow', String(over));
}

document.addEventListener('DOMContentLoaded', function () {
  buildBoxes();
  waitReady().then(function () {
    readSizes();
    layout();
  });
});
</script>
</body></html>
'''


MATH_SPAN = '<span class="km">{tex}</span>'


def node_html(raw, assets_rel):
    """保留 ZhiMap 自己的富文本标记（粗体/颜色），只把图片改指本地、公式标成 span.km。"""
    if not raw:
        return ''
    t = _katex_to_tex(str(raw), MATH_SPAN)
    t = t.replace('\u200b', '')
    t = re.sub(r'<span class="km">(.*?)</span>',
               lambda m: '<span class="km">' + m.group(1).replace('&', '&amp;').replace('<', '&lt;') + '</span>',
               t, flags=re.S)
    t = re.sub(r'<script\b.*?</script>', '', t, flags=re.S | re.I)
    t = re.sub(r'\son\w+\s*=\s*"[^"]*"', '', t, flags=re.I)
    t = re.sub(r"\son\w+\s*=\s*'[^']*'", '', t, flags=re.I)

    def local(m):
        whole, src = m.group(0), m.group(1)
        name = Path(src.split('?')[0]).name
        if src.startswith('/res/') or (src.startswith('http') and SITE in src):
            return whole.replace(src, f'{assets_rel}/{name}')
        return whole

    return IMG_TAG.sub(local, t)


def build_tree(node, assets_rel, side=None):
    return {
        't': node_html(node.get('title'), assets_rel),
        'k': node_html(node.get('content'), assets_rel),
        'l': (node.get('link') or '')[:120],
        'side': node.get('side') or side or 'right',
        'c': [build_tree(c, assets_rel, side) for c in (node.get('children') or [])],
    }


def theme_bg(mind_map):
    try:
        theme = json.loads(mind_map.get('theme') or '{}')
    except Exception:
        theme = {}
    return theme.get('mapBgColor') or '#FFFFFF'


def make_html(mind_map, assets_rel):
    tree = (mind_map.get('trees') or [{}])[0]
    data = json.dumps({'root': build_tree(tree, assets_rel)}, ensure_ascii=False)
    html = TEMPLATE
    for k, v in (('__TITLE__', root_title(mind_map) or 'ZhiMap'),
                 ('__DATA__', data),
                 ('__HGAP__', str(H_GAP)),
                 ('__VGAP__', str(V_GAP)),
                 ('__PAD__', str(PAD)),
                 ('__MAXW__', str(MAX_TEXT_W)),
                 ('__MAXIMG__', str(MAX_IMG_W)),
                 ('__BG__', theme_bg(mind_map))):
        html = html.replace(k, v)
    return html


def find_chrome():
    for p in CHROME_CANDIDATES:
        if Path(p).exists():
            return p
    for name in ('chrome', 'msedge'):
        w = shutil.which(name)
        if w:
            return w
    raise SystemExit('找不到 Chrome / Edge，无法渲染')


def run_chrome(chrome, args, timeout=300):
    return subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-sandbox',
                           '--hide-scrollbars'] + args,
                          capture_output=True, text=True, encoding='utf-8', errors='replace',
                          timeout=timeout)


def canvas_size(dom):
    m = re.search(r'data-canvas="(\d+),(\d+)"', dom)
    if not m:
        raise RuntimeError('页面未产出画布尺寸（排版脚本可能报错）')
    raw = re.search(r'data-badmath="(\d+)"', dom)
    return int(m.group(1)), int(m.group(2)), int(raw.group(1)) if raw else -1


def trim_to_content(png_path, bg, margin=24):
    """截图窗口比画布略大时，按背景色裁掉多余边，再补一圈留白。"""
    from PIL import Image, ImageChops
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(png_path).convert('RGB')
    diff = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L')
    bbox = diff.point(lambda p: 255 if p > 12 else 0).getbbox()
    if not bbox:
        return im.size
    im = im.crop(bbox)
    out = Image.new('RGB', (im.width + margin * 2, im.height + margin * 2), bg)
    out.paste(im, (margin, margin))
    out.save(png_path)
    return out.size


def render_one(chrome, json_path, out_png, assets_rel, max_px, scale, html_dir=None):
    j = json.loads(Path(json_path).read_text(encoding='utf-8'))
    mm = j['data']['mindMap']
    bg = theme_bg(mm)
    tmp = Path(html_dir or tempfile.mkdtemp(prefix='zmrender_'))
    tmp.mkdir(parents=True, exist_ok=True)
    hp = tmp / (Path(json_path).stem + '.html')
    hp.write_text(make_html(mm, assets_rel), encoding='utf-8')
    url = hp.resolve().as_uri()

    dom = run_chrome(chrome, ['--virtual-time-budget=30000', '--dump-dom', url])
    w, h, rawmath = canvas_size(dom.stdout)
    eff = min(scale, max(1.0, max_px / max(w, h)))
    # 窗口给足余量，实际尺寸交给 PIL 裁剪，避免两次运行排版差几像素导致裁切
    shot = run_chrome(chrome, ['--virtual-time-budget=30000',
                               f'--window-size={w + 120},{h + 120}',
                               f'--force-device-scale-factor={eff:.2f}',
                               f'--screenshot={Path(out_png).resolve()}', url])
    if not Path(out_png).exists():
        raise RuntimeError('截图失败: ' + (shot.stderr or '')[-300:])
    final = trim_to_content(out_png, bg)
    return {'w': w, 'h': h, 'scale': round(eff, 2), 'px': final, 'rawmath': rawmath}


def main():
    ap = argparse.ArgumentParser(description='ZhiMap 导图 -> 完全展开的高清 PNG')
    ap.add_argument('json_dir')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--assets-rel', default='', help='HTML 里图片的路径前缀；留空则自动取 <json目录>/assets 或同级 assets 的绝对 file:/// 路径')
    ap.add_argument('--max-px', type=int, default=9000, help='输出图最长边目标上限：超出就降倍率，但最低 1:1，超大图仍会更长')
    ap.add_argument('--scale', type=float, default=2.0, help='目标倍率（device scale factor）')
    ap.add_argument('--only', help='只渲染文件名含此关键字的导图')
    ap.add_argument('--keep-html', action='store_true', help='把中间 HTML 留在输出目录的 _html/ 下')
    args = ap.parse_args()

    chrome = find_chrome()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html_dir = str(out / '_html') if args.keep_html else None
    assets_rel = args.assets_rel
    if not assets_rel:
        jd = Path(args.json_dir)
        assets_dir = next((d for d in (jd / 'assets', jd.parent / 'assets') if d.is_dir()), None)
        assets_rel = assets_dir.resolve().as_uri() if assets_dir else ''
        print(f'图片前缀: {assets_rel or "(未找到 assets 目录)"}')

    files = sorted(Path(args.json_dir).glob('*.json'))
    if args.only:
        files = [f for f in files if args.only.lower() in f.name.lower()]
    done = 0
    for f in files:
        j = json.loads(f.read_text(encoding='utf-8'))
        mm = j['data']['mindMap']
        uuid = re.search(r'__([0-9a-f]{16,})', f.name).group(1)
        base = safe_name(root_title(mm) or mm.get('title'), f.stem) + '__' + uuid
        try:
            info = render_one(chrome, f, out / (base + '.png'), assets_rel,
                              args.max_px, args.scale, html_dir)
            flag = '' if not info['rawmath'] else f'  未排版公式:{info["rawmath"]}'
            print(f'[OK] {base[:44]:<44} 画布{info["w"]}x{info["h"]} x{info["scale"]} -> '
                  f'{info["px"][0]}x{info["px"][1]}{flag}')
            done += 1
        except Exception as e:
            print(f'[FAIL] {f.name}: {e}')
    print(f'\n完成：{done}/{len(files)} 张，输出目录 {out}')


if __name__ == '__main__':
    main()
