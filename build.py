"""Build multi-page HTML book site from Markdown chapters with dark/light theme toggle."""
import re
from pathlib import Path

SRC = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\output\book-yuanli")
OUT = Path(__file__).parent

CHAPTERS = [
    ("ch00-preface",             "preface",              "前言",                    "Preface"),
    ("ch01-two-engines",         "two-engines",          "第一章：两种引擎",        "Ch1: Two Engines"),
    ("ch02-anatomy-of-fear",     "anatomy-of-fear",      "第二章：恐惧的解剖",      "Ch2: Anatomy of Fear"),
    ("ch03-inertia-of-karma",    "inertia-of-karma",     "第三章：业力的惯性",      "Ch3: Inertia of Karma"),
    ("ch04-nature-of-aspiration","nature-of-aspiration",  "第四章：愿力的本质",      "Ch4: Nature of Aspiration"),
    ("ch05-reactive-to-responsive","reactive-to-responsive","第五章：从反应到回应",  "Ch5: Reactive to Responsive"),
    ("ch06-stress-paradox",      "stress-paradox",       "第六章：适度压力的悖论",  "Ch6: The Stress Paradox"),
    ("ch07-daily-practice",      "daily-practice",       "第七章：愿力的日常实践",  "Ch7: Daily Practice"),
    ("ch08-aspiration-in-orgs",  "aspiration-in-orgs",   "第八章：组织中的愿力",    "Ch8: Aspiration in Orgs"),
    ("ch09-connecting-to-greater","connecting-to-greater","第九章：与更大的东西连接","Ch9: Connecting to Greater"),
]

BOOK_TITLE_ZH = "愿力：从恐惧驱动到内在驱动的认知转型"
BOOK_TITLE_EN = "Aspiration: From Fear-Driven to Inner-Driven"


def md_to_html(md: str) -> str:
    mermaid_blocks, code_blocks = [], []

    def save_mermaid(m):
        idx = len(mermaid_blocks)
        mermaid_blocks.append(m.group(1).strip())
        return f"<!--MERMAID_{idx}-->"

    def save_code(m):
        idx = len(code_blocks)
        lang = m.group(1) or ""
        code = m.group(2).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        code_blocks.append(f'<pre><code class="lang-{lang}">{code}</code></pre>')
        return f"<!--CODE_{idx}-->"

    md = re.sub(r"```mermaid\s*\n(.*?)```", save_mermaid, md, flags=re.DOTALL)
    md = re.sub(r"```(\w*)\s*\n(.*?)```", save_code, md, flags=re.DOTALL)

    def inline(t):
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
        return t

    lines = md.split("\n")
    out = []
    tbl, lst, bq = [], [], []

    def flush_tbl():
        if not tbl: return
        h = '<div class="tbl"><table>\n'
        for i, r in enumerate(tbl):
            cells = [c.strip() for c in r.strip("|").split("|")]
            if i == 0:
                h += "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>\n"
            elif i == 1: continue
            else:
                h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>\n"
        h += "</tbody></table></div>"
        out.append(h); tbl.clear()

    def flush_lst():
        if not lst: return
        out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>"); lst.clear()

    def flush_bq():
        if not bq: return
        out.append('<blockquote>' + "<br>".join(inline(l) for l in bq) + "</blockquote>"); bq.clear()

    for line in lines:
        s = line.strip()
        if s.startswith("|") and "|" in s[1:]:
            flush_lst(); flush_bq(); tbl.append(s); continue
        elif tbl: flush_tbl()
        if s.startswith("> "):
            flush_lst(); bq.append(s[2:]); continue
        elif bq: flush_bq()
        if re.match(r"^- ", s):
            flush_tbl(); lst.append(s[2:]); continue
        elif lst and s == "": flush_lst(); continue
        elif lst: flush_lst()
        if re.match(r"^\d+\. ", s):
            out.append(f"<p class='num-item'>{inline(s)}</p>"); continue
        if s.startswith("<!--"): out.append(s); continue
        if s.startswith("# "): out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("## "): out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("### "): out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s == "---": out.append("<hr>")
        elif s == "": out.append("")
        else: out.append(f"<p>{inline(s)}</p>")

    flush_tbl(); flush_lst(); flush_bq()
    result = "\n".join(out)
    for i, b in enumerate(mermaid_blocks):
        result = result.replace(f"<!--MERMAID_{i}-->", f'<div class="mermaid">{b}</div>')
    for i, b in enumerate(code_blocks):
        result = result.replace(f"<!--CODE_{i}-->", b)
    return result


# --------------- CSS with dark + light theme ---------------
CSS = """
:root{--bg:#0d1117;--bg2:#161b22;--bg3:#1c2333;--tx:#e6edf3;--tx2:#8b949e;--ac:#7c3aed;--ac2:#a78bfa;--bd:#30363d;--gn:#3fb950;--or:#d29922;--strong:#fff;--bq-bg:rgba(124,58,237,.08);--hover-bg:rgba(124,58,237,.06)}

[data-theme="light"]{--bg:#f8f9fa;--bg2:#ffffff;--bg3:#e9ecef;--tx:#1a1a2e;--tx2:#495057;--ac:#6d28d9;--ac2:#5b21b6;--bd:#dee2e6;--gn:#198754;--or:#b45309;--strong:#0f0f23;--bq-bg:rgba(109,40,217,.06);--hover-bg:rgba(109,40,217,.04)}

*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:-apple-system,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--tx);line-height:1.8;display:flex;min-height:100vh;transition:background .3s,color .3s}
.side{width:260px;min-width:260px;background:var(--bg2);border-right:1px solid var(--bd);position:fixed;top:0;left:0;height:100vh;overflow-y:auto;z-index:100;transition:transform .3s,background .3s;padding:20px 0}
.side-hd{padding:0 16px 16px;border-bottom:1px solid var(--bd);margin-bottom:8px}
.side-hd h1{font-size:1.15rem;color:var(--ac2);letter-spacing:2px}
.side-hd p{font-size:.72rem;color:var(--tx2);margin-top:3px}
.toc a{display:block;padding:8px 16px;color:var(--tx2);text-decoration:none;font-size:.85rem;border-left:3px solid transparent;transition:all .2s}
.toc a:hover,.toc a.cur{background:var(--bg3);color:var(--tx);border-left-color:var(--ac)}
.side-bottom{padding:12px 16px;border-top:1px solid var(--bd);margin-top:8px;display:flex;flex-direction:column;gap:10px}
.lang-sw{display:flex;gap:8px}
.lang-sw a{padding:4px 12px;border-radius:4px;font-size:.78rem;text-decoration:none;color:var(--tx2);border:1px solid var(--bd);transition:all .2s}
.lang-sw a.act{background:var(--ac);color:#fff;border-color:var(--ac)}
.theme-toggle{display:flex;align-items:center;gap:8px;cursor:pointer;padding:6px 12px;border-radius:6px;border:1px solid var(--bd);background:var(--bg3);color:var(--tx2);font-size:.78rem;transition:all .2s;user-select:none}
.theme-toggle:hover{border-color:var(--ac);color:var(--tx)}
.theme-toggle .icon{font-size:1rem;line-height:1}
.main{margin-left:260px;flex:1;max-width:820px;padding:36px 44px 100px;transition:margin .3s}
h1{font-size:1.7rem;margin:28px 0 14px;color:var(--ac2);border-bottom:2px solid var(--bd);padding-bottom:8px}
h2{font-size:1.3rem;margin:24px 0 10px;color:var(--tx)}
h3{font-size:1.05rem;margin:18px 0 6px;color:var(--ac2)}
p{margin:8px 0}
hr{border:none;border-top:1px solid var(--bd);margin:24px 0}
strong{color:var(--strong)}
em{color:var(--ac2);font-style:italic}
code{background:var(--bg3);padding:1px 5px;border-radius:3px;font-size:.86em;color:var(--or)}
pre{background:var(--bg3);padding:14px;border-radius:7px;overflow-x:auto;margin:14px 0;border:1px solid var(--bd);transition:background .3s}
pre code{background:none;padding:0;color:var(--tx);font-size:.83rem}
a{color:var(--ac2)}
.tbl{overflow-x:auto;margin:14px 0}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{background:var(--bg3);color:var(--ac2);padding:8px 12px;text-align:left;border-bottom:2px solid var(--ac);font-weight:600}
td{padding:7px 12px;border-bottom:1px solid var(--bd)}
tr:hover td{background:var(--hover-bg)}
ul{margin:8px 0 8px 22px}
li{margin:3px 0}
li::marker{color:var(--ac)}
blockquote{border-left:4px solid var(--ac);padding:10px 18px;margin:14px 0;background:var(--bq-bg);border-radius:0 7px 7px 0;color:var(--tx2);font-style:italic;transition:background .3s}
.mermaid{background:var(--bg2);padding:18px;border-radius:9px;margin:18px 0;border:1px solid var(--bd);text-align:center;transition:background .3s}
.ch-nav{display:flex;justify-content:space-between;margin-top:40px;padding-top:16px;border-top:1px solid var(--bd)}
.ch-nav a{color:var(--ac2);text-decoration:none;padding:6px 14px;border:1px solid var(--bd);border-radius:5px;font-size:.88rem;transition:all .2s}
.ch-nav a:hover{background:var(--bg3);border-color:var(--ac)}
.ham{display:none;position:fixed;top:10px;left:10px;z-index:200;background:var(--bg2);border:1px solid var(--bd);color:var(--tx);padding:6px 10px;border-radius:5px;font-size:1.1rem;cursor:pointer;transition:background .3s}
.num-item{margin:4px 0 4px 20px}
@media(max-width:860px){.side{transform:translateX(-100%)}.side.open{transform:translateX(0)}.main{margin-left:0;padding:20px 16px 60px}.ham{display:block}h1{font-size:1.3rem}}
"""

# --------------- Theme toggle JS ---------------
THEME_JS = """
<script>
(function(){
  var saved = localStorage.getItem('yuanli-theme');
  if(saved) document.documentElement.setAttribute('data-theme', saved);
  else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches)
    document.documentElement.setAttribute('data-theme', 'light');
})();
function toggleTheme(){
  var el = document.documentElement;
  var cur = el.getAttribute('data-theme');
  var next = cur === 'light' ? 'dark' : 'light';
  el.setAttribute('data-theme', next);
  localStorage.setItem('yuanli-theme', next);
  updateToggleBtn();
  reinitMermaid(next);
}
function updateToggleBtn(){
  var btns = document.querySelectorAll('.theme-toggle');
  var isLight = document.documentElement.getAttribute('data-theme') === 'light';
  btns.forEach(function(b){
    b.querySelector('.icon').textContent = isLight ? '\\u263E' : '\\u2600';
    b.querySelector('.label').textContent = isLight ? '\\u6DF1\\u8272\\u6A21\\u5F0F' : '\\u6D45\\u8272\\u6A21\\u5F0F';
  });
}
function reinitMermaid(theme){
  if(typeof mermaid === 'undefined') return;
  var isDark = theme !== 'light';
  mermaid.initialize({
    startOnLoad: false,
    theme: isDark ? 'dark' : 'default',
    themeVariables: isDark
      ? {primaryColor:'#7c3aed',primaryTextColor:'#fff',lineColor:'#8b949e',secondaryColor:'#1c2333'}
      : {primaryColor:'#6d28d9',primaryTextColor:'#1a1a2e',lineColor:'#495057',secondaryColor:'#e9ecef'}
  });
  document.querySelectorAll('.mermaid').forEach(function(el){
    var code = el.getAttribute('data-mermaid');
    if(!code) return;
    el.removeAttribute('data-processed');
    el.innerHTML = code;
  });
  mermaid.run();
}
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.mermaid').forEach(function(el){
    el.setAttribute('data-mermaid', el.textContent.trim());
  });
  var theme = document.documentElement.getAttribute('data-theme') || 'dark';
  var isDark = theme !== 'light';
  mermaid.initialize({
    startOnLoad: true,
    theme: isDark ? 'dark' : 'default',
    themeVariables: isDark
      ? {primaryColor:'#7c3aed',primaryTextColor:'#fff',lineColor:'#8b949e',secondaryColor:'#1c2333'}
      : {primaryColor:'#6d28d9',primaryTextColor:'#1a1a2e',lineColor:'#495057',secondaryColor:'#e9ecef'}
  });
  updateToggleBtn();
});
</script>
"""

THEME_TOGGLE_HTML = '<button class="theme-toggle" onclick="toggleTheme()"><span class="icon">&#9728;</span><span class="label">浅色模式</span></button>'


def build_chapter_page(ch_idx, slug, content_html, lang):
    prev_link = ""
    next_link = ""
    if ch_idx > 0:
        ps = CHAPTERS[ch_idx-1][1]
        pl = CHAPTERS[ch_idx-1][2] if lang == "zh" else CHAPTERS[ch_idx-1][3]
        prev_link = f'<a href="{ps}.html?lang={lang}">\u2190 {pl}</a>'
    if ch_idx < len(CHAPTERS)-1:
        ns = CHAPTERS[ch_idx+1][1]
        nl = CHAPTERS[ch_idx+1][2] if lang == "zh" else CHAPTERS[ch_idx+1][3]
        next_link = f'<a href="{ns}.html?lang={lang}">{nl} \u2192</a>'

    toc = ""
    for i, (_, s, zh, en) in enumerate(CHAPTERS):
        label = zh if lang == "zh" else en
        cls = ' class="cur"' if i == ch_idx else ""
        toc += f'<a href="{s}.html?lang={lang}"{cls}>{i:02d} {label}</a>\n'

    zh_cls = "act" if lang == "zh" else ""
    en_cls = "act" if lang == "en" else ""

    title = (CHAPTERS[ch_idx][2] if lang == "zh" else CHAPTERS[ch_idx][3])
    book = BOOK_TITLE_ZH if lang == "zh" else BOOK_TITLE_EN
    toggle_label = "浅色模式" if lang == "zh" else "Light Mode"

    return f"""<!DOCTYPE html>
<html lang="{"zh-CN" if lang=="zh" else "en"}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | {book}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<button class="ham" onclick="document.querySelector('.side').classList.toggle('open')">&#9776;</button>
<nav class="side">
  <div class="side-hd">
    <h1>{"愿 力" if lang=="zh" else "ASPIRATION"}</h1>
    <p>{"从恐惧驱动到内在驱动" if lang=="zh" else "Fear-Driven \u2192 Inner-Driven"}</p>
  </div>
  <div class="toc">
{toc}
  </div>
  <div class="side-bottom">
    <div class="lang-sw">
      <a href="{slug}.html?lang=zh" class="{zh_cls}">中文</a>
      <a href="{slug}.html?lang=en" class="{en_cls}">English</a>
    </div>
    {THEME_TOGGLE_HTML}
  </div>
</nav>
<main class="main">
{content_html}
<div class="ch-nav">
  {prev_link or "<span></span>"}
  {next_link or "<span></span>"}
</div>
</main>
{THEME_JS}
</body>
</html>"""


def build_index():
    zh_links = ""
    en_links = ""
    for i, (_, slug, zh, en) in enumerate(CHAPTERS):
        zh_links += f'    <a href="{slug}.html?lang=zh"><span class="num">{i:02d}</span> {zh}</a>\n'
        en_links += f'    <a href="{slug}.html?lang=en"><span class="num">{i:02d}</span> {en}</a>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{BOOK_TITLE_ZH}</title>
<style>
{CSS}
.side{{display:none}}
.main{{margin-left:0;max-width:900px;margin:0 auto;padding:60px 40px}}
.hero{{text-align:center;margin-bottom:48px}}
.hero h1{{font-size:2.4rem;border:none;color:var(--ac2);margin-bottom:8px}}
.hero .sub{{font-size:1rem;color:var(--tx2);margin-bottom:4px}}
.hero .sub2{{font-size:.85rem;color:var(--tx2)}}
.theme-bar{{display:flex;justify-content:center;margin-bottom:20px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin:32px 0}}
@media(max-width:700px){{.cols{{grid-template-columns:1fr}}.hero h1{{font-size:1.6rem}}}}
.col h2{{font-size:1.1rem;margin-bottom:12px;color:var(--ac2)}}
.col a{{display:flex;align-items:center;gap:10px;padding:10px 14px;color:var(--tx2);text-decoration:none;border-radius:6px;margin:2px 0;transition:all .2s;font-size:.9rem}}
.col a:hover{{background:var(--bg3);color:var(--tx)}}
.col a .num{{color:var(--ac);font-weight:700;font-size:.8rem;min-width:22px}}
.pillars{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:40px 0}}
@media(max-width:700px){{.pillars{{grid-template-columns:1fr}}}}
.pill{{background:var(--bg2);border:1px solid var(--bd);border-radius:10px;padding:20px;text-align:center;transition:background .3s}}
.pill .icon{{font-size:1.6rem;margin-bottom:6px}}
.pill h3{{color:var(--ac2);font-size:.95rem;margin:4px 0}}
.pill p{{color:var(--tx2);font-size:.8rem}}
.companion{{background:var(--bg2);border:1px solid var(--bd);border-radius:10px;padding:24px;margin:40px 0;text-align:center;transition:background .3s}}
.companion p{{color:var(--tx2);font-size:.88rem}}
.companion a{{color:var(--ac2)}}
</style>
</head>
<body>
<main class="main">
<div class="hero">
  <h1>愿 力</h1>
  <p class="sub">{BOOK_TITLE_ZH}</p>
  <p class="sub2">{BOOK_TITLE_EN}</p>
</div>
<div class="theme-bar">
  {THEME_TOGGLE_HTML}
</div>

<div class="cols">
  <div class="col">
    <h2>📖 中文目录</h2>
{zh_links}
  </div>
  <div class="col">
    <h2>📖 Table of Contents</h2>
{en_links}
  </div>
</div>

<div class="pillars">
  <div class="pill">
    <div class="icon">🔥</div>
    <h3>诊断篇 Diagnosis</h3>
    <p>Ch01-03: 两种引擎 · 恐惧解剖 · 业力惯性</p>
  </div>
  <div class="pill">
    <div class="icon">🔄</div>
    <h3>转换篇 Transformation</h3>
    <p>Ch04-06: 愿力本质 · 反应到回应 · 压力悖论</p>
  </div>
  <div class="pill">
    <div class="icon">🌱</div>
    <h3>应用篇 Application</h3>
    <p>Ch07-09: 日常实践 · 组织愿力 · 意义连接</p>
  </div>
</div>

<div class="companion">
  <p>📚 姊妹书 Companion Book: <a href="https://wanweiok.github.io/book-metacognition">《元认知：AI 时代的人类最后护城河》</a></p>
  <p>《元认知》回答 HOW（如何思考）· 《愿力》回答 WHY（为何行动）</p>
</div>
</main>
{THEME_JS}
</body>
</html>"""


def main():
    for i, (file_prefix, slug, zh_title, en_title) in enumerate(CHAPTERS):
        for lang in ("zh", "en"):
            md_file = SRC / f"{file_prefix}-{lang}.md"
            md = md_file.read_text(encoding="utf-8")
            content = md_to_html(md)
            html = build_chapter_page(i, slug, content, lang)
            if lang == "zh":
                (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
                print(f"  {slug}.html (zh)")
            else:
                (OUT / f"{slug}-en.html").write_text(html, encoding="utf-8")
                print(f"  {slug}-en.html (en)")

    for _, slug, _, _ in CHAPTERS:
        zh_html = (OUT / f"{slug}.html").read_text(encoding="utf-8")
        redirect_script = f'<script>if(new URLSearchParams(location.search).get("lang")==="en")location.replace("{slug}-en.html")</script>\n'
        zh_html = zh_html.replace("<head>", "<head>\n" + redirect_script, 1)
        (OUT / f"{slug}.html").write_text(zh_html, encoding="utf-8")

    idx = build_index()
    (OUT / "index.html").write_text(idx, encoding="utf-8")
    print("  index.html")
    print(f"\nDone! {len(CHAPTERS)*2 + 1} files generated.")


if __name__ == "__main__":
    main()
