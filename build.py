"""Build a single-page HTML book from Markdown chapter files."""
import re
from pathlib import Path

BOOK_DIR = Path(__file__).parent
CHAPTERS = [
    "ch00-preface-zh.md",
    "ch01-two-engines-zh.md",
    "ch02-anatomy-of-fear-zh.md",
    "ch03-inertia-of-karma-zh.md",
    "ch04-nature-of-aspiration-zh.md",
    "ch05-reactive-to-responsive-zh.md",
    "ch06-stress-paradox-zh.md",
    "ch07-daily-practice-zh.md",
    "ch08-aspiration-in-orgs-zh.md",
    "ch09-connecting-to-greater-zh.md",
]

CHAPTER_TITLES = [
    ("前言", ""),
    ("第一章", "两种引擎"),
    ("第二章", "恐惧的解剖"),
    ("第三章", "业力的惯性"),
    ("第四章", "愿力的本质"),
    ("第五章", "从反应到回应"),
    ("第六章", "适度压力的悖论"),
    ("第七章", "愿力的日常实践"),
    ("第八章", "组织中的愿力"),
    ("第九章", "与更大的东西连接"),
]


def md_to_html(md: str) -> str:
    mermaid_blocks = []

    def replace_mermaid(m):
        idx = len(mermaid_blocks)
        mermaid_blocks.append(m.group(1).strip())
        return f"<!--MERMAID_{idx}-->"

    md = re.sub(r"```mermaid\s*\n(.*?)```", replace_mermaid, md, flags=re.DOTALL)

    code_blocks = []

    def replace_code(m):
        idx = len(code_blocks)
        lang = m.group(1) or ""
        code = m.group(2).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        code_blocks.append(f'<pre><code class="language-{lang}">{code}</code></pre>')
        return f"<!--CODE_{idx}-->"

    md = re.sub(r"```(\w*)\s*\n(.*?)```", replace_code, md, flags=re.DOTALL)

    lines = md.split("\n")
    html_lines = []
    in_table = False
    in_list = False
    in_blockquote = False
    table_rows = []
    list_items = []
    bq_lines = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        out = '<div class="table-wrap"><table>\n'
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if i == 0:
                out += "<thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead>\n<tbody>\n"
            elif i == 1:
                continue
            else:
                out += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>\n"
        out += "</tbody></table></div>"
        html_lines.append(out)
        table_rows = []
        in_table = False

    def flush_list():
        nonlocal in_list, list_items
        if not list_items:
            return
        html_lines.append("<ul>" + "".join(f"<li>{inline(li)}</li>" for li in list_items) + "</ul>")
        list_items = []
        in_list = False

    def flush_bq():
        nonlocal in_blockquote, bq_lines
        if not bq_lines:
            return
        html_lines.append('<blockquote class="bq">' + "<br>".join(inline(l) for l in bq_lines) + "</blockquote>")
        bq_lines = []
        in_blockquote = False

    def inline(text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
        return text

    for line in lines:
        stripped = line.strip()

        img_match = re.match(r'!\[(.+?)\]\((.+?)\)', stripped)
        if img_match:
            if in_table: flush_table()
            if in_list: flush_list()
            if in_blockquote: flush_bq()
            alt = img_match.group(1)
            src = img_match.group(2)
            svg_path = BOOK_DIR / src
            if svg_path.exists() and src.endswith('.svg'):
                svg_raw = svg_path.read_text(encoding='utf-8')
                svg_raw = re.sub(r'<\?xml[^>]+\?>\s*', '', svg_raw)
                html_lines.append(f'<figure class="diagram"><div class="svg-wrap">{svg_raw}</div><figcaption>{alt}</figcaption></figure>')
            else:
                html_lines.append(f'<figure class="diagram"><img src="{src}" alt="{alt}"><figcaption>{alt}</figcaption></figure>')
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            if in_list:
                flush_list()
            if in_blockquote:
                flush_bq()
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            flush_table()

        if stripped.startswith("> "):
            if in_list:
                flush_list()
            in_blockquote = True
            bq_lines.append(stripped[2:])
            continue
        elif in_blockquote:
            flush_bq()

        if re.match(r"^- ", stripped):
            if in_table:
                flush_table()
            in_list = True
            list_items.append(stripped[2:])
            continue
        elif in_list and stripped == "":
            flush_list()
            continue
        elif in_list:
            flush_list()

        if stripped.startswith("<!--MERMAID_") or stripped.startswith("<!--CODE_"):
            html_lines.append(stripped)
            continue
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{inline(stripped[4:])}</h3>")
        elif stripped == "---":
            html_lines.append("<hr>")
        elif stripped == "":
            html_lines.append("")
        else:
            html_lines.append(f"<p>{inline(stripped)}</p>")

    if in_table:
        flush_table()
    if in_list:
        flush_list()
    if in_blockquote:
        flush_bq()

    result = "\n".join(html_lines)

    for i, block in enumerate(mermaid_blocks):
        result = result.replace(f"<!--MERMAID_{i}-->", f'<div class="mermaid">{block}</div>')
    for i, block in enumerate(code_blocks):
        result = result.replace(f"<!--CODE_{i}-->", block)

    return result


def build():
    toc_html = ""
    chapters_html = ""

    for i, (fname, (prefix, subtitle)) in enumerate(zip(CHAPTERS, CHAPTER_TITLES)):
        md = (BOOK_DIR / fname).read_text(encoding="utf-8")
        ch_id = f"ch{i:02d}"
        label = f"{prefix}：{subtitle}" if subtitle else prefix
        toc_html += f'<a href="#{ch_id}" class="toc-item" onclick="showChapter(\'{ch_id}\')">{label}</a>\n'
        content = md_to_html(md)
        chapters_html += f'<section id="{ch_id}" class="chapter">\n{content}\n</section>\n'

    html = TEMPLATE.replace("{{TOC}}", toc_html).replace("{{CHAPTERS}}", chapters_html)
    out_path = BOOK_DIR / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Built: {out_path} ({out_path.stat().st_size:,} bytes)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>愿力：从恐惧驱动到内在驱动的认知转型</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #1c2333;
  --text: #e6edf3;
  --text2: #8b949e;
  --accent: #7c3aed;
  --accent2: #a78bfa;
  --border: #30363d;
  --green: #3fb950;
  --orange: #d29922;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  padding: 24px 0;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
  transition: transform 0.3s;
}
.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}
.sidebar-header h1 {
  font-size: 1.2rem;
  color: var(--accent2);
  font-weight: 700;
  letter-spacing: 2px;
}
.sidebar-header p {
  font-size: 0.75rem;
  color: var(--text2);
  margin-top: 4px;
}
.toc-item {
  display: block;
  padding: 10px 20px;
  color: var(--text2);
  text-decoration: none;
  font-size: 0.88rem;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.toc-item:hover, .toc-item.active {
  background: var(--bg3);
  color: var(--text);
  border-left-color: var(--accent);
}
.main {
  margin-left: 280px;
  flex: 1;
  max-width: 820px;
  padding: 40px 48px 120px;
}
.chapter { display: none; }
.chapter.active { display: block; }
h1 { font-size: 1.8rem; margin: 32px 0 16px; color: var(--accent2); border-bottom: 2px solid var(--border); padding-bottom: 10px; }
h2 { font-size: 1.35rem; margin: 28px 0 12px; color: var(--text); }
h3 { font-size: 1.1rem; margin: 20px 0 8px; color: var(--accent2); }
p { margin: 10px 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 28px 0; }
strong { color: #fff; }
em { color: var(--accent2); font-style: italic; }
code { background: var(--bg3); padding: 2px 6px; border-radius: 4px; font-size: 0.88em; color: var(--orange); }
pre { background: var(--bg3); padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid var(--border); }
pre code { background: none; padding: 0; color: var(--text); font-size: 0.85rem; }
a { color: var(--accent2); }
.table-wrap { overflow-x: auto; margin: 16px 0; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th { background: var(--bg3); color: var(--accent2); padding: 10px 14px; text-align: left; border-bottom: 2px solid var(--accent); font-weight: 600; }
td { padding: 9px 14px; border-bottom: 1px solid var(--border); }
tr:hover td { background: rgba(124, 58, 237, 0.06); }
ul { margin: 10px 0 10px 24px; }
li { margin: 4px 0; }
li::marker { color: var(--accent); }
blockquote.bq {
  border-left: 4px solid var(--accent);
  padding: 12px 20px;
  margin: 16px 0;
  background: rgba(124, 58, 237, 0.08);
  border-radius: 0 8px 8px 0;
  color: var(--text2);
  font-style: italic;
}
.mermaid {
  background: var(--bg2);
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
  border: 1px solid var(--border);
  text-align: center;
}
.diagram {
  margin: 24px 0;
  text-align: center;
}
.svg-wrap {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  display: inline-block;
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
}
.svg-wrap svg { max-width: 100%; height: auto; }
.diagram figcaption {
  font-size: 0.82rem;
  color: var(--text2);
  margin-top: 8px;
  font-style: italic;
}
.hamburger {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 200;
  background: var(--bg2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 1.2rem;
  cursor: pointer;
}
@media (max-width: 860px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .main { margin-left: 0; padding: 24px 20px 80px; }
  .hamburger { display: block; }
  h1 { font-size: 1.4rem; }
}
.chapter-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 48px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
.chapter-nav a {
  color: var(--accent2);
  text-decoration: none;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.9rem;
}
.chapter-nav a:hover { background: var(--bg3); border-color: var(--accent); }
</style>
</head>
<body>
<button class="hamburger" onclick="toggleSidebar()">☰</button>
<nav class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h1>愿 力</h1>
    <p>从恐惧驱动到内在驱动的认知转型</p>
  </div>
{{TOC}}
</nav>
<main class="main" id="main">
{{CHAPTERS}}
</main>
<script>
const chapters = document.querySelectorAll('.chapter');
const tocItems = document.querySelectorAll('.toc-item');
const chapterIds = Array.from(chapters).map(c => c.id);

function showChapter(id) {
  chapters.forEach(c => c.classList.remove('active'));
  tocItems.forEach(t => t.classList.remove('active'));
  const ch = document.getElementById(id);
  if (ch) {
    ch.classList.add('active');
    const idx = chapterIds.indexOf(id);
    if (tocItems[idx]) tocItems[idx].classList.add('active');
    addChapterNav(idx);
    window.scrollTo(0, 0);
    mermaid.run({ querySelector: '#' + id + ' .mermaid' });
  }
  const sb = document.getElementById('sidebar');
  if (window.innerWidth <= 860) sb.classList.remove('open');
  history.replaceState(null, '', '#' + id);
}

function addChapterNav(idx) {
  document.querySelectorAll('.chapter-nav').forEach(n => n.remove());
  const ch = chapters[idx];
  const nav = document.createElement('div');
  nav.className = 'chapter-nav';
  const prev = idx > 0 ? `<a href="#" onclick="event.preventDefault();showChapter('${chapterIds[idx-1]}')">← 上一章</a>` : '<span></span>';
  const next = idx < chapterIds.length - 1 ? `<a href="#" onclick="event.preventDefault();showChapter('${chapterIds[idx+1]}')">下一章 →</a>` : '<span></span>';
  nav.innerHTML = prev + next;
  ch.appendChild(nav);
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

mermaid.initialize({ startOnLoad: false, theme: 'dark', themeVariables: { primaryColor: '#7c3aed', primaryTextColor: '#fff', lineColor: '#8b949e', secondaryColor: '#1c2333' }});

const hash = location.hash.replace('#', '') || 'ch00';
showChapter(hash);
</script>
</body>
</html>"""

if __name__ == "__main__":
    build()
