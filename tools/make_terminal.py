"""プロフィール用の「仰々しいターミナル」アニメーション SVG を作る。

使い方: python tools/make_terminal.py   → assets/terminal.svg

仰々しい起動ログ → ACCESS GRANTED → 画面クリア → ドット絵の 🥺 がコンソールいっぱいに、進捗ゲージのように上から1段ずつ出る。
SMIL アニメーションだけで動かしている（README の <img> 内では JavaScript が動かないため）。
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
W, H = 820, 452
X0 = 24
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
PROMPT = "yuseisland@github"
COMMAND = "sudo ./show-profile --all --force --verbose"
LOG_WIDTH = 50  # 「[ OK ]」の手前までの桁数（等幅なので文字数でそろう）

CLEAR_AT = 8.0               # 画面をクリアする時刻
PIXELS_FROM, PIXELS_DUR = 8.3, 4.0  # ドット絵が上から出ていく時間帯
PROMPT_AT = 12.8             # 最後のプロンプト

parts = []


def appear(at):
    """at 秒で表示されるようにする（それまでは透明）。"""
    return f'opacity="0"><set attributeName="opacity" to="1" begin="{at}s" fill="freeze"/'


def text_line(y, spans, at=None, cls="mono"):
    inner = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' for c, s in spans)
    if at is None:
        parts.append(f'<text class="{cls}" x="{X0}" y="{y}" xml:space="preserve">{inner}</text>')
    else:
        parts.append(f'<text class="{cls}" x="{X0}" y="{y}" xml:space="preserve" {appear(at)}>{inner}</text>')


def log_line(y, at, stamp, label, extra=""):
    head = f"[{stamp:>10}] {label} "
    dots = "." * max(3, LOG_WIDTH - len(head))
    text_line(y, [("dim", f"[{stamp:>10}] "), ("w", label + " "), ("dim", dots + " "),
                  ("dim", "["), ("ok", " OK "), ("dim", "]"), ("dim", extra)], at)


# --- ウィンドウ ---
parts.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="#0d1117" stroke="#30363d"/>')
parts.append(f'<path d="M0.5,36 V12.5 a12,12 0 0 1 12,-12 H{W - 12.5} a12,12 0 0 1 12,12 V36 Z" fill="#161b22"/>')
for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    parts.append(f'<circle cx="{22 + 20 * i}" cy="18" r="6" fill="{c}"/>')
parts.append(f'<text class="mono dim" x="{W / 2}" y="23" text-anchor="middle" font-size="13">'
             f'{PROMPT} — show-profile — 80×24</text>')

# ここから下のログは CLEAR_AT でまとめて消す
parts.append("<g>")
parts.append(f'<set attributeName="opacity" to="0" begin="{CLEAR_AT}s" fill="freeze"/>')

# --- 1行目：コマンドを1文字ずつ打ち込む（プロンプトと同じ行に続けるので、フォントが変わってもずれない） ---
y = 70
typed = "".join(
    f'<tspan class="w" fill-opacity="0"><set attributeName="fill-opacity" to="1" begin="{0.4 + i * 0.032:.3f}s" '
    f'fill="freeze"/>{escape(ch)}</tspan>' for i, ch in enumerate(COMMAND))
parts.append(f'<text class="mono" x="{X0}" y="{y}" xml:space="preserve"><tspan class="p">{PROMPT}</tspan>'
             f'<tspan class="w">:~$ </tspan>{typed}</text>')

text_line(94, [("dim", "[sudo] password for yuseisland: "), ("w", "************")], 2.0)

# --- 起動ログ ---
log_line(122, 2.5, "0.0012", "Booting profile engine")
log_line(146, 2.85, "0.2048", "Loading neural modules")
log_line(170, 3.2, "0.4096", "Mounting /dev/brain", " (read-only)")
log_line(194, 3.55, "0.8192", "Synchronizing with satellites")

# 復号の進捗バー：同じ文字位置に「░」と「█」を重ね、█ 側を左から見せていく
y = 218
head = f"[{'1.6384':>10}] Decrypting identity "
bar = 24
text_line(y, [("dim", f"[{'1.6384':>10}] "), ("w", "Decrypting identity "), ("dim", "[" + "░" * bar + "]")], 3.9)
parts.append(f'<clipPath id="bar"><rect x="{X0}" y="{y - 16}" height="22" width="0">'
             f'<animate attributeName="width" from="0" to="{W}" begin="3.9s" dur="1.5s" fill="freeze"/></rect></clipPath>')
parts.append(f'<text class="mono" x="{X0}" y="{y}" clip-path="url(#bar)" xml:space="preserve" {appear(3.9)}>'
             f'<tspan fill-opacity="0">{escape(head)}[</tspan><tspan class="p">{"█" * bar}</tspan></text>')
text_line(y, [("dim", " " * (len(head) + bar + 2)), ("ok", " 100%")], 5.4)

log_line(242, 5.8, "3.2768", "Cross-checking 3,141,592 records")

# --- ACCESS GRANTED（何度か点滅してから表示） ---
parts.append(f'<text class="mono granted" x="{W / 2}" y="296" text-anchor="middle" filter="url(#glow)" opacity="0">'
             f'<animate attributeName="opacity" values="0;1;0;1;0;1" keyTimes="0;0.2;0.4;0.6;0.8;1" '
             f'begin="6.5s" dur="0.9s" fill="freeze"/>██  ACCESS GRANTED  ██</text>')
parts.append("</g>")

# --- ドット絵の 🥺（32x32）---
N = 32
COLORS = {
    "k": "#8a4a00",  # 輪郭
    "Y": "#ffe27a",  # 顔（ハイライト）
    "y": "#ffcd3c",  # 顔
    "o": "#f5a623",  # 顔（影）
    "e": "#7a4300",  # 眉・口
    "d": "#2b1a10",  # 目
    "w": "#ffffff",  # 目のハイライト
    "b": "#5a3d2b",  # 目の下側（うるうる）
    "t": "#a9d4ff",  # 涙のきらめき
    "m": "#ff9e7a",  # 頬
}
grid = [[None] * N for _ in range(N)]


def inside(x, y):
    return (x - 15.5) ** 2 + (y - 15.5) ** 2 <= 14.6 ** 2


for y in range(N):
    for x in range(N):
        if not inside(x, y):
            continue
        if not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            grid[y][x] = "k"
        elif (x - 10) ** 2 + (y - 8) ** 2 < 24:
            grid[y][x] = "Y"
        elif (x - 15.5) ** 2 + (y - 15.5) ** 2 > 11.5 ** 2 and x + y > 33:
            grid[y][x] = "o"
        else:
            grid[y][x] = "y"

EYE = [
    "..ddd..",
    ".ddddd.",
    "dwwdddd",
    "dwwwddd",
    "dwwdddd",
    "ddddddd",
    "dddddwd",
    ".dbbbd.",
    "..ttt..",
]
for ox in (7, 18):
    for dy, row in enumerate(EYE):
        for dx, ch in enumerate(row):
            if ch != ".":
                grid[12 + dy][ox + dx] = ch
# 困り眉（内側が上がる）
for x, y in [(6, 10), (7, 10), (8, 9), (9, 9), (10, 8), (11, 8)]:
    grid[y][x] = "e"
    grid[y][31 - x] = "e"
# への字の口
for x in range(14, 18):
    grid[24][x] = "e"
grid[25][13] = grid[25][18] = "e"
# 頬
for x in (5, 6, 25, 26):
    grid[22][x] = "m"

CELL = 12
GAP = 1.2
ox = (W - N * CELL) / 2
oy = 40 + ((H - 44) - N * CELL) / 2

# 上から1段ずつ見せる：表示範囲（clipPath）の高さを1マス分ずつ伸ばす
cells = [(x, y, grid[y][x]) for y in range(N) for x in range(N) if grid[y][x]]
heights = ";".join(str(CELL * r) for r in range(N + 1))
parts.append(f'<clipPath id="reveal"><rect x="{ox:.1f}" y="{oy:.1f}" width="{N * CELL}" height="0">'
             f'<animate attributeName="height" values="{heights}" calcMode="discrete" '
             f'begin="{PIXELS_FROM}s" dur="{PIXELS_DUR}s" fill="freeze"/></rect></clipPath>')
rects = "".join(
    f'<rect x="{ox + x * CELL + GAP / 2:.1f}" y="{oy + y * CELL + GAP / 2:.1f}" '
    f'width="{CELL - GAP:.1f}" height="{CELL - GAP:.1f}" fill="{COLORS[ch]}"/>' for x, y, ch in cells)
parts.append(f'<g clip-path="url(#reveal)">{rects}</g>')

# --- 最後のプロンプトと点滅カーソル（左下。カーソルも同じ行の文字にする） ---
parts.append(f'<text class="mono" x="{X0}" y="{H - 22}" xml:space="preserve" {appear(PROMPT_AT)}>'
             f'<tspan class="p">{PROMPT}</tspan><tspan class="w">:~$ </tspan><tspan class="w">'
             f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" '
             f'begin="{PROMPT_AT}s" repeatCount="indefinite"/>█</tspan></text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"
     aria-label="仰々しい起動ログが流れたあと、ドット絵の🥺がコンソールいっぱいにじわじわ浮かび上がるターミナル">
<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style>
  .mono {{ font-family: {MONO}; font-size: 15px; }}
  .p {{ fill: #f7a9b9; }}
  .w {{ fill: #e6edf3; }}
  .dim {{ fill: #6e7681; }}
  .ok {{ fill: #3fb950; font-weight: 700; }}
  .granted {{ fill: #ff4d6d; font-size: 24px; font-weight: 700; letter-spacing: 2px; }}
</style>
{chr(10).join(parts)}
</svg>
'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print("saved", OUT, f"({OUT.stat().st_size // 1024} KB, {len(cells)} dots)")
