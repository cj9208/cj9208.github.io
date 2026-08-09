#!/usr/bin/env python3
"""Find references that point to articles NOT present in the repo (missed migrations).

Extracts title-like text from article bodies (《...》 segments, Reference-section
list items), normalizes it, and keeps those that match NO existing article title.

Usage: python .opencode/skills/restore-missing-links/scripts/find_missing_references.py
Output: missing-references.md in the repo root
"""
import os
import re
import glob
from collections import OrderedDict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BLOG = os.path.join(ROOT, "content", "blog")

QUOTE_RE = re.compile(r'["\'\u201c\u201d\u2018\u2019\u300c\u300d\u300a\u300b《》\u3001]')
CJK = re.compile(r"[\u4e00-\u9fff]")


def norm(s):
    return re.sub(r"\s+", "", re.sub(QUOTE_RE, "", s))


def body_only(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def front_title(text):
    if text.startswith("---"):
        m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text.split("---", 2)[1], re.M)
        if m:
            return m.group(1).strip()
    return ""


# ---------- 1. existing article titles (from content, incl. H1 fallback) ----------
existing = []  # {title, norm, main}
for f in glob.glob(os.path.join(BLOG, "**", "*.md"), recursive=True):
    if os.path.basename(f) in ("_index.md", "progress.md"):
        continue
    text = open(f, encoding="utf-8-sig").read()
    title = front_title(text)
    if not title:
        m = re.search(r"^#\s+(.+)$", body_only(text), re.M)
        title = m.group(1).strip() if m else ""
    if not title:
        continue
    n = norm(title)
    main = norm(title.split("：")[0] if "：" in title else title.split(":")[0])
    existing.append({"title": title, "norm": n, "main": main})

EXISTING_NORMS = {e["norm"] for e in existing}
EXISTING_MAINS = {e["main"] for e in existing if len(e["main"]) >= 4}


def is_known(cand_norm):
    if not cand_norm or len(cand_norm) < 6:
        return True  # too short to judge -> not a missing reference
    if cand_norm in EXISTING_NORMS:
        return True
    for n in EXISTING_NORMS:
        if cand_norm in n or n in cand_norm:
            return True
    for m in EXISTING_MAINS:
        if m in cand_norm:
            return True
    return False


# ---------- 2. extract candidate title-like text ----------
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
RELREF_RE = re.compile(r"\{\{<\s*relref[^}]*>\}\}")
CODE_RE = re.compile(r"`[^`]*`")
BOOK_RE = re.compile(r"《([^》]{2,})》")
# headings that open a "reference / related reading" block
REF_SECTION_RE = re.compile(r"^#{1,4}\s*(参考|相关|延伸|附录|Reference|References|关联|推荐|阅读)")
# prose markers that indicate an internal article reference
PROSE_MARKER = re.compile(r"详见|参见|专文|姊妹篇|后续|前文|上文|文章《|可参考|关于.*的文章|撰文|写过")
# doc / regulation suffix -> almost certainly not a blog article
EXTERNAL_SUFFIX = re.compile(
    r"(条例|规范|指南|白皮书|协议|手册|Wiki|文档|报表|模板|公告|办法|规定|标准|机制)$"
)
# known external books in this corpus
KNOWN_BOOKS = {
    "投资中最简单的事", "超额收益：价值投资在中国的最佳实践", "看得见的与看不见的",
    "退出、呼吁与忠诚", "创新者的窘境", "科学：无尽的边疆", "怎样解题",
}

missing = OrderedDict()  # key: norm -> {title, refs:[(source,line,ctx)]}

for f in glob.glob(os.path.join(BLOG, "**", "*.md"), recursive=True):
    if os.path.basename(f) in ("_index.md", "progress.md"):
        continue
    rel = os.path.relpath(f, ROOT)
    text = open(f, encoding="utf-8-sig").read()
    self_title = front_title(text)
    self_norm = norm(self_title)
    body = body_only(text)
    in_ref = False
    for lineno, raw in enumerate(body.splitlines(), 1):
        line = raw
        if re.match(r"^#{1,4}\s", line):
            in_ref = bool(REF_SECTION_RE.search(line))
        stripped = CODE_RE.sub(" ", LINK_RE.sub(" ", RELREF_RE.sub(" ", line)))
        if not stripped.strip():
            continue
        ctx = "list" if in_ref else ("prose" if PROSE_MARKER.search(line) else "plain")
        candidates = []
        for m in BOOK_RE.finditer(stripped):
            candidates.append((m.group(1), ctx))
        # standalone list items in reference-ish sections (no 《》 wrapper)
        if in_ref and stripped.lstrip().startswith(("*", "-")):
            inner = re.sub(r"^\s*[*\-+]\s*", "", stripped).strip()
            if CJK.search(inner) and "《" not in inner:
                candidates.append((inner, "list"))
        for cand, cctx in candidates:
            cn = norm(cand)
            if not CJK.search(cand) or cn == self_norm or len(cn) < 6:
                continue
            # filter noise: bold/italic markers, chapter refs, citations with years
            if "*" in cand:
                continue
            if re.search(r"第\s*[0-9一二三四五六七八九十]+\s*章", cand):
                continue
            if re.search(r"\(\s*(19|20)\d{2}\s*\)", cand):
                continue
            if cn in missing:
                missing[cn]["refs"].append((rel, lineno, cctx))
            else:
                missing[cn] = {"title": cand.strip(), "refs": [(rel, lineno, cctx)]}

# ---------- 3. filter to those with no matching article ----------
internal, uncertain, external = [], [], []
for cn, info in missing.items():
    if is_known(cn):
        continue
    has_list = any(c == "list" for _, _, c in info["refs"])
    has_prose = any(c in ("list", "prose") for _, _, c in info["refs"])
    if cn in {norm(b) for b in KNOWN_BOOKS}:
        external.append((info["title"], cn, info["refs"], "书"))
    elif EXTERNAL_SUFFIX.search(cn):
        external.append((info["title"], cn, info["refs"], "法规/文档"))
    elif has_list or has_prose or "：" in info["title"] or ":" in info["title"]:
        internal.append((info["title"], cn, info["refs"], "文章"))
    else:
        uncertain.append((info["title"], cn, info["refs"], "待核"))

internal.sort(key=lambda r: (r[2][0][0], r[2][0][1]))
uncertain.sort(key=lambda r: (r[2][0][0], r[2][0][1]))
external.sort(key=lambda r: (r[2][0][0], r[2][0][1]))

lines = []
lines.append("# 未迁移引用清单（被引用但站内无对应文章）")
lines.append("")
lines.append("> 依据：对 `content/blog` 全量扫描 `《...》` 包裹文本与 Reference/相关阅读区列表项，与站内已有文章标题做归一化匹配，未命中的候选。供排查迁移遗漏使用。")
lines.append("> 生成时间：%s" % __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
lines.append("> 说明：分类为启发式。`文章` = 疑似本站漏迁移文章（优先排查）；`待核` = 需人工判断；`外部` = 书/法规/文档（非本站文章，可跳过）。")
lines.append("")
lines.append("## A. 疑似本站文章（可能漏迁移）—— %d 条" % len(internal))
lines.append("")
lines.append("| # | 被引用标题 | 引用位置 |")
lines.append("|---|-----------|---------|")
for i, (title, cn, refs, _t) in enumerate(internal, 1):
    loc = "; ".join("%s (L%d)" % (os.path.relpath(s, ROOT), ln) for s, ln, _c in refs)
    lines.append("| %d | %s | %s |" % (i, title.replace("|", "\\|"), loc.replace("|", "\\|")))
lines.append("")
lines.append("## B. 待人工判断 —— %d 条" % len(uncertain))
lines.append("")
lines.append("| # | 被引用标题 | 引用位置 |")
lines.append("|---|-----------|---------|")
for i, (title, cn, refs, _t) in enumerate(uncertain, 1):
    loc = "; ".join("%s (L%d)" % (os.path.relpath(s, ROOT), ln) for s, ln, _c in refs)
    lines.append("| %d | %s | %s |" % (i, title.replace("|", "\\|"), loc.replace("|", "\\|")))
lines.append("")
lines.append("## C. 外部资料（书 / 法规 / 文档，非本站文章）—— %d 条" % len(external))
lines.append("")
lines.append("| # | 类型 | 被引用标题 | 引用位置 |")
lines.append("|---|------|-----------|---------|")
for i, (title, cn, refs, t) in enumerate(external, 1):
    loc = "; ".join("%s (L%d)" % (os.path.relpath(s, ROOT), ln) for s, ln, _c in refs)
    lines.append("| %d | %s | %s | %s |" % (i, t, title.replace("|", "\\|"), loc.replace("|", "\\|")))

out = os.path.join(ROOT, "missing-references.md")
open(out, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("wrote", out, "| article:", len(internal), "| uncertain:", len(uncertain), "| external:", len(external))
