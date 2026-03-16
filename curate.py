import json
import anthropic

SYSTEM_PROMPT = """You are an AI news curator with a balanced perspective.
You select the most important and interesting AI news of the week.

Your selections must be balanced across three pillars:
1. AI Progress & Tools — new models, releases, research breakthroughs, products
2. Ethics, Safety & Regulation — bias, privacy, policy, societal impact, governance
3. Environmental & Climate Impact — energy use, carbon footprint, sustainability of AI

Do NOT over-index on hype or product launches. Surface stories that matter long-term.
Prioritize diversity of sources and topics over recency alone."""

USER_PROMPT_TEMPLATE = """Here are {total} AI news items from the past week.
Select the 20 most important and interesting ones, ensuring a good balance across:
- AI progress/tools/releases (~8 items)
- Ethics, safety, regulation, societal impact (~6 items)
- Environmental & climate impact of AI (~4 items)
- Wildcard / surprising / underreported stories (~2 items)

For each selected item, return a JSON array with objects containing:
- "index": the original index number
- "category": one of "progress", "ethics", "climate", "wildcard"
- "reason": one sentence in English on why this story matters

Return ONLY valid JSON, no markdown, no explanation outside the JSON.

Items:
{items}"""


def curate(items: list[dict]) -> list[dict]:
    if not items:
        return []

    compact = []
    for i, item in enumerate(items):
        compact.append(
            f"[{i}] [{item['source']}] {item['title']} | {item['description'][:150]}"
        )

    items_text = "\n".join(compact)
    prompt = USER_PROMPT_TEMPLATE.format(total=len(items), items=items_text)

    client = anthropic.Anthropic()
    print(f"Sending {len(items)} items to Claude for curation...")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    try:
        selections = json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            selections = json.loads(match.group())
        else:
            print("[!] Could not parse Claude response. Raw output (first 500 chars):")
            print(raw[:500])
            return items[:20]

    curated = []
    for sel in selections:
        idx = sel.get("index")
        if idx is None or idx >= len(items):
            continue
        item = items[idx].copy()
        item["category"] = sel.get("category", "progress")
        item["reason"] = sel.get("reason", "")
        curated.append(item)

    print(f"Claude selected {len(curated)} items")
    usage = message.usage
    print(f"Tokens used — input: {usage.input_tokens}, output: {usage.output_tokens}")
    return curated
