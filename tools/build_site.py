"""產生靜態網站：python3 tools/build_site.py  → 輸出到 site/"""
import html, os, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site"

def esc(s): return html.escape(s, quote=False)

# ---------- 共用內容 ----------
TOPPINGS = {
    "瑪格麗特口味": ["番茄糊　適量", "新鮮羅勒　適量（可用九層塔替代）", "黑胡椒　適量",
                 "Mozzarella 乳酪絲　適量", "橄欖油　適量（出爐後淋）"],
    "青醬野菇口味": ["青醬　適量", "新鮮蘑菇　適量", "鴻喜菇　適量", "黑胡椒　適量",
                 "Mozzarella 乳酪絲　適量", "松露油　適量（出爐後淋）"],
}
TOOLS = [
    ("烤箱", "可達 250°C，建議有上下火功能"),
    ("攪拌機", "KitchenAid、Sunmix 等桌上型攪拌機皆可（亦可手揉，時間約加倍）"),
    ("冰箱", "需具備冷藏功能"),
    ("烘焙工具", "鋼盆、橡膠刮板、計時器、電子秤（可秤到 0.1g）、塑膠發酵盒、烤盤、烤焙紙、噴水瓶、溫度計"),
]

def shape_steps(chung=True):
    tip = ("中筋麵團延展性好但筋度較弱，拉的時候不要過度用力，以免破洞；中央拍平一些可承裝更多鋪料。"
           if chung else "中央拍平一些，可以承裝更多鋪料。")
    return [
        ("**整形**：由中心向外拍開麵團，再用手輕輕向外拉開。", tip),
        ("**瑪格麗特披薩**：將適量番茄糊抹平在麵團上，外圍留空。撒上新鮮羅勒、黑胡椒、乳酪絲。", "若沒有羅勒，也可以用九層塔替代。"),
        ("**青醬野菇披薩**：將適量青醬抹平在麵團上，外圍留空。鋪上乳酪絲、各式菇類、黑胡椒。", "鋪料時野菇放在最上層，熟得比較快。"),
    ]

def bake_steps(minutes, chung=True):
    s = [("烤箱提早 **30 分鐘** 預熱至上下火 250°C（烤盤一起預熱效果更好）。", None),
         (f"將披薩放上烤盤，放在烤箱**最上層**，烘烤約 **{minutes} 分鐘**，至邊緣金黃、乳酪冒泡。",
          "若烤箱無上下火，統一設定 250°C。" + ("中筋麵粉上色比高筋稍慢，看顏色決定是否多烤 1 分鐘。" if chung else "")),
         ("出爐後依個人口味淋上橄欖油、松露油，完成！", None)]
    return s

FLOUR_NOTE = ("關於麵粉替換",
    "本配方使用 **嘉禾牌 中筋粉心麵粉**（一般超市即可購得），取代原配方的日清高筋麵粉與百合花法國粉。"
    "中筋麵粉吸水率比高筋／法國粉低，因此**水量已下修**，攪拌時間也縮短，避免麵筋打斷。"
    "每批麵粉吸水性略有差異，建議**保留 15g 水**，視麵團軟硬再分次加入。")

# ---------- 三份食譜 ----------
RECIPES = [
  dict(
    slug="original", badge="原版", title="瑪格麗特、青醬野菇披薩",
    variant="原版配方・液種", pdf=None,
    summary="課程原配方。日清高筋麵粉做隔夜液種，主麵團使用百合花法國粉，風味層次最豐富。",
    flour="日清高筋＋百合花法國粉", time="前一天液種＋隔天約 3 小時", yield_="4 個披薩",
    notes=[],
    ingredients=[
      ("液種（前一天製作，自製）", [
        ("高筋麵粉", "Bread Flour", "50", "300", "烘焙材料行", "推薦品牌：日清", False),
        ("水", "Water", "50", "300", "", "飲用水即可", False),
        ("低糖乾酵母", "Instant Dry Yeast", "0.05", "0.3", "烘焙材料行", "若使用新鮮酵母，份量為 3 倍", False)]),
      ("主麵團", [
        ("液種", "Poolish", "100.05", "600.3", "自製", "上方培養完成的液種全部使用", False),
        ("百合花法國粉", "LYS D'OR", "50", "300", "烘焙材料行", "", False),
        ("鹽", "Salt", "2.2", "13.2", "超市／大賣場", "", False),
        ("低糖乾酵母", "Instant Dry Yeast", "0.4", "2.4", "超市／大賣場", "若使用新鮮酵母，份量為 3 倍", False),
        ("水", "Water", "25", "150", "", "", False),
        ("橄欖油", "Olive Oil", "3", "18", "超市／大賣場", "", False)]),
    ],
    total=("180.65", "1083.9", "分割 4 份，每份 250g"),
    baker="以麵粉總重 600g（液種高筋麵粉 300g ＋ 百合花法國粉 300g）為 100%。例：低糖酵母 0.4% → 600g × 0.4% = 2.4g。",
    timeline=None,
    method=[
      ("事前準備：液種製作（前一天）", [
        ("將低糖乾酵母加入常溫水中，攪拌至溶解。", "水：酵母 = 100：0.1，水量可依麵粉吸水性增減。"),
        ("加入高筋麵粉攪拌均勻，需攪拌至無明顯顆粒。", "液種配方 麵粉：水：酵母 = 100：100：0.1。"),
        ("以 25°C 室溫培養，發酵隔夜約 **15 小時**。", "大約膨脹至 3–4 倍，建議使用有刻度的透明容器，方便觀察。"),
        ("培養完成狀態：有泡泡形成，體積膨脹 3–4 倍，具明顯發酵香氣。", None),
        ("最佳使用時機：接近發酵過度，液種有約 1–2cm 高度落差時，風味最佳。", None)]),
      ("攪拌與基本發酵", [
        ("將液種與水秤在一起，方便容易取出液種。", None),
        ("倒入所有材料後，**慢速攪拌 5 分鐘**。", None),
        ("改**快速攪拌約 8–10 分鐘**。攪拌完成麵團終溫約 **26°C**。", None),
        ("把不規則的麵團向中心收合。", "容器噴油、手上沾水，避免麵團沾黏。"),
        ("**基本發酵**：室溫 25–30°C 發酵 45 分鐘，翻面。", None),
        ("翻面後再發酵 **45 分鐘**（由外往內壓折 3–4 折）。基本發酵共 90 分鐘。", None),
        ("發酵完成狀態：觸感蓬鬆柔軟，可以輕易戳進麵團並留下指痕。", None)]),
      ("分割滾圓", [
        ("取出麵團分割成 4 份，每份 **250g**。", "撒手粉（高筋麵粉），避免麵團沾黏。"),
        ("滾圓：將麵團周邊的裂口向內收整，往中心捏合即可。", None)]),
      ("整形與最後發酵", [("**最後發酵**：冷藏至少 1 小時，可以超過 1 小時，但不建議放隔夜。", None)]
                      + shape_steps(False)),
      ("入爐烘烤", bake_steps("3–5", False)),
    ],
    extra=None),
  dict(
    slug="chiaher-poolish", badge="嘉禾・液種", title="瑪格麗特、青醬野菇披薩",
    variant="嘉禾中筋麵粉版・液種", pdf="chiaher-poolish.pdf",
    summary="把兩種麵粉都換成超市就買得到的嘉禾中筋粉心麵粉，保留隔夜液種，水量與攪拌時間配合中筋調整。",
    flour="嘉禾中筋粉心麵粉", time="前一天液種＋隔天約 3 小時", yield_="4 個披薩",
    notes=[FLOUR_NOTE],
    ingredients=[
      ("液種（前一天製作，自製）", [
        ("嘉禾中筋粉心麵粉", "All-Purpose Flour", "50", "300", "超市／大賣場", "取代原本的日清高筋麵粉", True),
        ("水", "Water", "50", "300", "", "飲用水即可", False),
        ("低糖乾酵母", "Instant Dry Yeast", "0.05", "0.3", "烘焙材料行", "若使用新鮮酵母，份量為 3 倍", False)]),
      ("主麵團", [
        ("液種", "Poolish", "100.05", "600.3", "自製", "上方培養完成的液種全部使用", False),
        ("嘉禾中筋粉心麵粉", "All-Purpose Flour", "50", "300", "超市／大賣場", "取代原本的百合花法國粉", True),
        ("鹽", "Salt", "2.2", "13.2", "超市／大賣場", "", False),
        ("低糖乾酵母", "Instant Dry Yeast", "0.4", "2.4", "超市／大賣場", "若使用新鮮酵母，份量為 3 倍", False),
        ("水", "Water", "20", "120", "", "原配方 150g，中筋吸水較低故下修；另備 15g 調整水", True),
        ("橄欖油", "Olive Oil", "3", "18", "超市／大賣場", "", False)]),
    ],
    total=("175.65", "1053.9", "總含水率 70%（原配方 75%）；分割 4 份，每份約 260g"),
    baker="以麵粉總重 600g（液種 300g ＋ 主麵團 300g）為 100%。例：低糖酵母 0.4% → 600g × 0.4% = 2.4g。",
    timeline=None,
    method=[
      ("事前準備：液種製作（前一天）", [
        ("將低糖乾酵母加入常溫水中，攪拌至溶解。", None),
        ("加入嘉禾中筋麵粉攪拌均勻，至無明顯粉粒。", "液種配方 麵粉：水：酵母 = 100：100：0.1。"),
        ("以 25°C 室溫培養，發酵隔夜約 **14–15 小時**。", "中筋液種發酵力稍弱、也較稀，膨脹約 2.5–3 倍即可。"),
        ("培養完成狀態：表面佈滿泡泡、體積明顯膨脹、有發酵香氣。", None),
        ("最佳使用時機：頂端剛開始微微塌陷（約 1cm 落差）時，風味最佳。", None)]),
      ("攪拌與基本發酵", [
        ("將液種與主麵團的水秤在一起，方便把液種完整倒出。", None),
        ("倒入所有材料（橄欖油可最後加），**慢速攪拌 4 分鐘**。偏乾再分次加入調整水。", None),
        ("改**快速攪拌約 4–6 分鐘**，至麵團光滑、可拉出稍透光的薄膜。終溫約 **26°C**。",
         "中筋麵粉筋度較弱，快速攪拌時間比原配方（8–10 分鐘）短，勿過度攪拌。"),
        ("把麵團向中心收合，放入噴油的發酵盒。", "容器噴油、手上沾水，避免沾黏。"),
        ("**基本發酵**：室溫 25–28°C 發酵 45 分鐘後翻麵（由外往內壓折 3–4 折）。", None),
        ("翻麵後再發酵 **45 分鐘**，基本發酵共 90 分鐘。", None),
        ("發酵完成狀態：觸感蓬鬆柔軟，手指沾粉輕戳會留下指痕、緩慢回彈。", None)]),
      ("分割滾圓", [
        ("將麵團平均分割成 4 份，每份約 **260g**。", "手粉可使用嘉禾中筋麵粉。"),
        ("滾圓：將麵團周邊向內收整，往中心捏合，收口朝下。", None)]),
      ("整形與最後發酵", [("**最後發酵**：蓋好冷藏至少 1 小時（不建議隔夜）。整形前取出回溫約 15 分鐘，較好拉開。", None)]
                      + shape_steps(True)),
      ("入爐烘烤", bake_steps("4–6")),
    ],
    extra=None),
  dict(
    slug="chiaher-same-day", badge="嘉禾・當天快速", title="瑪格麗特、青醬野菇披薩",
    variant="嘉禾中筋麵粉版・當天快速發酵", pdf="chiaher-same-day.pdf",
    summary="不做隔夜液種，直接法一次攪拌，提高酵母並用溫水加速發酵，當天約 2.5 小時就能出爐。",
    flour="嘉禾中筋粉心麵粉", time="當天約 2.5 小時", yield_="4 個披薩",
    notes=[FLOUR_NOTE,
      ("快速版的改變",
       "① 不做隔夜液種，所有麵粉直接打成一個麵團（直接法）；② 酵母由 0.45% 提高到 **1%**，並使用約 **32°C 溫水**；"
       "③ 加 1% 糖幫助上色與酵母啟動；④ 最後發酵改為室溫鬆弛，不需冷藏。")],
    ingredients=[
      ("主麵團（一次攪拌完成）", [
        ("嘉禾中筋粉心麵粉", "All-Purpose Flour", "100", "600", "超市／大賣場", "取代原本的高筋麵粉＋法國粉", True),
        ("溫水（約 32°C）", "Warm Water", "68", "408", "", "另備 15g 調整水；夏天室溫高可改用常溫水", True),
        ("低糖乾酵母", "Instant Dry Yeast", "1", "6", "超市／大賣場", "若使用新鮮酵母，份量為 3 倍（18g）", True),
        ("鹽", "Salt", "2", "12", "超市／大賣場", "", False),
        ("細砂糖", "Sugar", "1", "6", "超市／大賣場", "新增：幫助上色與發酵", True),
        ("橄欖油", "Olive Oil", "3", "18", "超市／大賣場", "", False)]),
    ],
    total=("175", "1050", "分割 4 份，每份約 260g"),
    baker="以麵粉 600g 為 100%。例：酵母 1% → 600g × 1% = 6g。想做 2 個披薩，全部份量 ÷ 2 即可。",
    timeline=[("13:00", "秤料、攪拌", "約 15 分鐘"), ("13:15", "基本發酵", "共約 60 分鐘，30 分鐘時翻麵一次"),
              ("14:15", "分割滾圓", "約 10 分鐘"), ("14:25", "中間鬆弛＋預熱烤箱", "鬆弛 25–30 分鐘，同時預熱 250°C、準備鋪料"),
              ("14:55", "整形、鋪料", "約 10 分鐘"), ("15:05", "烘烤", "每批 4–6 分鐘，約 15:30 全部出爐")],
    method=[
      ("攪拌與基本發酵", [
        ("將低糖乾酵母、糖放入溫水中攪拌至溶解（約 5 分鐘，表面微微起泡）。", None),
        ("加入嘉禾中筋麵粉，**慢速攪拌 3 分鐘**至成團、無乾粉。偏乾再分次加入調整水。", None),
        ("加入鹽，慢速再攪拌 1 分鐘；最後加入橄欖油，攪拌至油被完全吸收。", None),
        ("改**快速攪拌約 4–5 分鐘**，至麵團光滑、可拉出稍透光的薄膜。終溫約 **27–28°C**。",
         "鹽晚一點加，酵母啟動更快；中筋麵團不要攪拌過久。"),
        ("把麵團向中心收合，放入噴油的發酵盒，蓋上蓋子。", "容器噴油、手上沾水，避免沾黏。"),
        ("**基本發酵**：溫暖處（28–30°C）發酵 30 分鐘，翻麵（壓折 3–4 折），再發酵約 30 分鐘。",
         "沒有發酵箱，可把麵團放進「未開啟」的烤箱，旁邊放一碗熱水保溫。"),
        ("發酵完成狀態：體積約 1.5–2 倍，觸感蓬鬆，手指沾粉輕戳會留下指痕、緩慢回彈。", None)]),
      ("分割滾圓與中間鬆弛", [
        ("將麵團平均分割成 4 份，每份約 **260g**。", "手粉可使用嘉禾中筋麵粉。"),
        ("滾圓：將麵團周邊向內收整，往中心捏合，收口朝下。", None),
        ("**中間鬆弛**：蓋上保鮮膜或濕布，室溫鬆弛 **25–30 分鐘**，至麵團變軟、容易拉開（不需冷藏）。此時開始預熱烤箱。",
         "若拉開時一直縮回，代表筋還太緊，再多鬆弛 10 分鐘。")]),
      ("整形與鋪料", shape_steps(True)),
      ("入爐烘烤", bake_steps("4–6")),
    ],
    extra=("風味小提醒", "快速版少了隔夜液種，麥香與層次會稍淡一些，但口感柔軟、當天就能吃到。"
           "若時間允許，可把分割滾圓後的麵團冷藏 2–4 小時再整形，風味會更好。")),
]

# ---------- HTML ----------
def md(s):
    """把 **粗體** 轉成 <strong>"""
    out, parts = [], esc(s).split("**")
    for i, p in enumerate(parts):
        out.append(f"<strong>{p}</strong>" if i % 2 else p)
    return "".join(out)

def page(title, body, desc, depth=0):
    pre = "../" * depth
    return f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}assets/style.css">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
</head>
<body>
{body}
<footer class="site-foot"><div class="wrap">披薩食譜筆記　·　配方依課程講義整理與改編</div></footer>
</body>
</html>
"""

def recipe_page(r):
    notes = "".join(f'<aside class="note"><h4>{esc(t)}</h4><p>{md(b)}</p></aside>' for t, b in r["notes"])
    rows = []
    for sec, items in r["ingredients"]:
        rows.append(f'<tr class="sec"><th colspan="4" scope="rowgroup">{esc(sec)}</th></tr>')
        for name, en, pct, g, src, note, chg in items:
            cls = ' class="chg"' if chg else ""
            sub = f"<small>{esc(src)}</small>" if src else ""
            rows.append(f'<tr{cls}><td class="name">{esc(name)}<span>{esc(en)}</span></td>'
                        f'<td class="num">{pct}</td><td class="num g">{g}</td>'
                        f'<td class="memo">{esc(note)}{sub}</td></tr>')
    tp, tg, tn = r["total"]
    rows.append(f'<tr class="total"><td class="name">麵團總重</td><td class="num">{tp}</td><td class="num g">{tg}</td><td class="memo">{esc(tn)}</td></tr>')
    table = f"""<div class="table-wrap"><table class="ing">
<thead><tr><th>食材</th><th class="num">烘焙%</th><th class="num">份量 (g)</th><th>提醒／購入</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    legend = '<p class="legend"><span class="dot"></span>紅字為與原配方不同之處</p>' if r["slug"] != "original" else ""

    timeline = ""
    if r["timeline"]:
        items = "".join(f'<li><time>{t}</time><div><b>{esc(a)}</b><span>{esc(b)}</span></div></li>' for t, a, b in r["timeline"])
        timeline = f'<section><h2>當天時程表 <em>以 13:00 開始為例</em></h2><ol class="timeline">{items}</ol></section>'

    tops = "".join(f'<div class="card"><h3>{esc(k)}</h3><ul>{"".join(f"<li>{esc(i)}</li>" for i in v)}</ul></div>'
                   for k, v in TOPPINGS.items())
    tools = "".join(f"<li><b>{esc(a)}</b>：{esc(b)}</li>" for a, b in TOOLS)

    steps_html = ""
    for i, (sec, steps) in enumerate(r["method"], 1):
        lis = "".join(f'<li>{md(s)}{f"<p class=tip>{md(t)}</p>" if t else ""}</li>' for s, t in steps)
        steps_html += f'<div class="step-group"><h3><span>{i:02d}</span>{esc(sec)}</h3><ol>{lis}</ol></div>'

    extra = f'<aside class="note"><h4>{esc(r["extra"][0])}</h4><p>{md(r["extra"][1])}</p></aside>' if r["extra"] else ""
    pdf = (f'<a class="btn" href="../pdf/{r["pdf"]}" download>下載 PDF</a>' if r["pdf"] else "")

    body = f"""
<header class="hero">
  <img src="../assets/cover.jpg" alt="瑪格麗特披薩與青醬野菇披薩成品" width="1100" height="613">
</header>
<main class="wrap recipe">
  <nav class="crumb"><a href="../">← 所有食譜</a></nav>
  <p class="badge">{esc(r["variant"])}</p>
  <h1>{esc(r["title"])}</h1>
  <p class="lead">{esc(r["summary"])}</p>
  <dl class="facts">
    <div><dt>份量</dt><dd>{esc(r["yield_"])}</dd></div>
    <div><dt>製作時程</dt><dd>{esc(r["time"])}</dd></div>
    <div><dt>麵粉</dt><dd>{esc(r["flour"])}</dd></div>
  </dl>
  <div class="actions">{pdf}<button class="btn ghost" onclick="window.print()">列印</button></div>
  {notes}
  <section><h2>食材準備</h2>{legend}{table}<p class="baker"><b>烘焙百分比</b>　{md(r["baker"])}份量超過小數點後兩位時，四捨五入到電子秤可量測的份量即可。</p></section>
  {timeline}
  <section><h2>鋪料 <em>各 2 個</em></h2><div class="cards">{tops}</div></section>
  <section><h2>器材工具</h2><ul class="tools">{tools}</ul></section>
  <section><h2>製作方法</h2>{steps_html}</section>
  <aside class="note blue"><p>享用提醒：披薩較不耐放，建議出爐後馬上享用。</p></aside>
  {extra}
</main>"""
    return page(f"{r['variant']}｜{r['title']}", body, r["summary"], depth=1)

def index_page():
    cards = ""
    for r in RECIPES:
        cards += f"""<a class="rcard" href="recipes/{r['slug']}.html">
  <img src="assets/thumb-{r['slug']}.jpg" alt="" width="520" height="520" loading="lazy">
  <div class="rbody"><span class="badge">{esc(r['badge'])}</span>
  <h2>{esc(r['title'])}</h2><p class="variant">{esc(r['variant'])}</p>
  <p>{esc(r['summary'])}</p>
  <dl><div><dt>麵粉</dt><dd>{esc(r['flour'])}</dd></div><div><dt>時程</dt><dd>{esc(r['time'])}</dd></div></dl>
  <span class="more">看食譜 →</span></div></a>"""
    body = f"""
<header class="home-head"><div class="wrap">
  <p class="eyebrow">Pizza Recipes</p>
  <h1>披薩食譜</h1>
  <p class="lead">瑪格麗特與青醬野菇披薩，三種做法：課程原版、嘉禾中筋麵粉液種版，以及當天就能出爐的快速發酵版。</p>
</div></header>
<main class="wrap"><div class="list">{cards}</div></main>"""
    return page("披薩食譜", body, "瑪格麗特、青醬野菇披薩的三種做法")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "recipes").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copytree(ROOT / "pdf", OUT / "pdf")
    (OUT / "index.html").write_text(index_page(), encoding="utf-8")
    for r in RECIPES:
        (OUT / "recipes" / f"{r['slug']}.html").write_text(recipe_page(r), encoding="utf-8")
    (OUT / "404.html").write_text(page("找不到頁面", '<main class="wrap recipe"><h1>找不到這個頁面</h1><p><a href="/">回到食譜列表</a></p></main>', "404"), encoding="utf-8")
    print("built", OUT)

if __name__ == "__main__":
    main()
