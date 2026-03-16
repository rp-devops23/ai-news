import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

CATEGORY_META = {
    "progress":  {"label": "AI Progress",           "color": "#7c3aed", "icon": "🚀"},
    "ethics":    {"label": "Ethics & Safety",        "color": "#0891b2", "icon": "⚖️"},
    "climate":   {"label": "Climate & Environment",  "color": "#059669", "icon": "🌍"},
    "wildcard":  {"label": "Wildcard",               "color": "#d97706", "icon": "✨"},
}


def _format_date(raw: str) -> str:
    if not raw:
        return ""
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            dt = datetime.strptime(raw[:25], fmt[:len(fmt)])
            return dt.strftime("%d %b %Y").lstrip("0")
        except ValueError:
            pass
    try:
        dt = parsedate_to_datetime(raw)
        return dt.strftime("%d %b %Y").lstrip("0")
    except Exception:
        pass
    return ""


def _extract_video_id(url: str) -> str | None:
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Weekly Digest</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:      #0f0f13;
      --surface: #18181f;
      --border:  #2a2a35;
      --text:    #e2e2f0;
      --muted:   #8888aa;
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      padding: 2rem 1rem 5rem;
    }}

    /* ── Header ── */
    header {{
      max-width: 1100px;
      margin: 0 auto 3rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.5rem;
    }}

    header h1 {{
      font-size: 2rem;
      font-weight: 700;
      background: linear-gradient(90deg, #a78bfa, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    header p {{
      color: var(--muted);
      margin-top: .5rem;
      font-size: .95rem;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: .6rem;
      margin-top: 1rem;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: .3rem;
      font-size: .75rem;
      font-weight: 600;
      padding: .25rem .65rem;
      border-radius: 999px;
      border: 1px solid currentColor;
      opacity: .85;
    }}

    /* ── Section ── */
    .section {{
      max-width: 1100px;
      margin: 0 auto 3.5rem;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .section-header h2 {{
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: .03em;
      text-transform: uppercase;
      color: var(--muted);
      white-space: nowrap;
    }}

    .section-rule {{
      flex: 1;
      height: 1px;
      background: var(--border);
    }}

    /* ── Grids ── */
    .video-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }}

    .article-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
      gap: 1.5rem;
    }}

    @media (max-width: 560px) {{
      .video-grid, .article-grid {{ grid-template-columns: 1fr; }}
    }}

    /* ── Cards ── */
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform .15s ease, border-color .15s ease;
    }}

    .card:hover {{
      transform: translateY(-3px);
      border-color: #44445a;
    }}

    .card-embed {{
      width: 100%;
      aspect-ratio: 16/9;
      border: none;
      background: #000;
      display: block;
    }}

    .card-thumb {{
      width: 100%;
      aspect-ratio: 16/9;
      object-fit: cover;
    }}

    .card-body {{
      padding: 1.1rem;
      display: flex;
      flex-direction: column;
      flex: 1;
      gap: .55rem;
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: .5rem;
    }}

    .source-tag {{
      font-size: .7rem;
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .06em;
    }}

    .card-title {{
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.45;
    }}

    .card-title a {{
      color: var(--text);
      text-decoration: none;
    }}

    .card-title a:hover {{ color: #a78bfa; }}

    .card-reason {{
      font-size: .85rem;
      color: var(--muted);
      line-height: 1.55;
      flex: 1;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      gap: .6rem;
      margin-top: .2rem;
    }}

    .pub-date {{
      font-size: .75rem;
      color: var(--muted);
    }}

    footer {{
      text-align: center;
      color: var(--muted);
      font-size: .8rem;
      margin-top: 2rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>⚡ AI Weekly Digest</h1>
    <p>20 stories that matter — curated by Claude · Week of {week}</p>
    <div class="legend">
      <span class="badge" style="color:#a78bfa">🚀 AI Progress</span>
      <span class="badge" style="color:#38bdf8">⚖️ Ethics &amp; Safety</span>
      <span class="badge" style="color:#34d399">🌍 Climate &amp; Environment</span>
      <span class="badge" style="color:#fbbf24">✨ Wildcard</span>
    </div>
  </header>

  <div class="section">
    <div class="section-header">
      <h2>▶ Videos</h2>
      <div class="section-rule"></div>
    </div>
    <div class="video-grid">
      {video_cards}
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>📰 Articles</h2>
      <div class="section-rule"></div>
    </div>
    <div class="article-grid">
      {article_cards}
    </div>
  </div>

  <footer>
    Generated on {generated_at} · Powered by Claude (Haiku) + RSS + YouTube feeds
  </footer>
</body>
</html>"""

CARD_TEMPLATE = """      <div class="card">
        {media}
        <div class="card-body">
          <div class="card-meta">
            <span class="source-tag">{source}</span>
            <span class="badge" style="color:{cat_color}">{cat_icon} {cat_label}</span>
          </div>
          <div class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
          <div class="card-reason">{reason}</div>
          <div class="card-footer">
            {pub_date_html}
          </div>
        </div>
      </div>"""


def _media_html(item: dict) -> str:
    if item.get("type") == "video":
        video_id = _extract_video_id(item.get("url", ""))
        if video_id:
            safe_title = item.get("title", "").replace('"', "'")
            return (
                f'        <iframe class="card-embed" '
                f'src="https://www.youtube.com/embed/{video_id}" '
                f'title="{safe_title}" '
                f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                f'gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>'
            )
    if item.get("thumbnail"):
        return f'        <img class="card-thumb" src="{item["thumbnail"]}" alt="" loading="lazy" />'
    return ""


def _build_card(item: dict) -> str:
    cat = item.get("category", "progress")
    meta = CATEGORY_META.get(cat, CATEGORY_META["progress"])
    pub_date = _format_date(item.get("published", ""))
    pub_date_html = f'<span class="pub-date">📅 {pub_date}</span>' if pub_date else ""

    return CARD_TEMPLATE.format(
        media=_media_html(item),
        source=item.get("source", ""),
        cat_color=meta["color"],
        cat_icon=meta["icon"],
        cat_label=meta["label"],
        url=item.get("url", "#"),
        title=item.get("title", "Untitled").replace("<", "&lt;").replace(">", "&gt;"),
        reason=item.get("reason", "").replace("<", "&lt;").replace(">", "&gt;"),
        pub_date_html=pub_date_html,
    )


def render(items: list[dict], output_path: str = "index.html") -> None:
    now = datetime.now(timezone.utc)
    week_str = now.strftime("%d %B %Y").lstrip("0")
    generated_at = now.strftime("%Y-%m-%d %H:%M UTC")

    videos   = [i for i in items if i.get("type") == "video"]
    articles = [i for i in items if i.get("type") != "video"]

    video_cards   = "\n".join(_build_card(i) for i in videos)
    article_cards = "\n".join(_build_card(i) for i in articles)

    html = HTML_TEMPLATE.format(
        week=week_str,
        generated_at=generated_at,
        video_cards=video_cards or "      <p style='color:var(--muted)'>No videos this week.</p>",
        article_cards=article_cards or "      <p style='color:var(--muted)'>No articles this week.</p>",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Page written to: {output_path}  ({len(videos)} videos, {len(articles)} articles)")
