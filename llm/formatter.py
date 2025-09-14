import random
import re
import html
from telegram.helpers import escape_markdown

style_bank = [
    "We looks for the Precious' whispers through the shadows.",
    "Fragile hobbitses, stumbling in darkness, craving knowledge they cannot grasp.",
    "Even Gollum's precious knows better than to trust hobbitcraft searches.",
    "Would Allen have asked this? No. He wielded wisdom, not mere queries."
]

def clean_html(text: str) -> str:
    """Strip away the hobbitish tags and uncurse any entities."""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)

def escape_url(url: str) -> str:
    """Escape only the characters in URLs that conflict with MarkdownV2."""
    return re.sub(r'([()\[\]\\_.*~`>#+-=|{}!])', r'\\\1', url)

def format_search_response(results: list[tuple[str, str, str]], max_entries: int = 3) -> str:
    """
    Format Brave search results with Gollum/Smeagol flair and MarkdownV2 escaping.
    """
    if not results:
        return escape_markdown("Gollum searched far and wide and found naught. Precious is displeased.", version=2)

    intro = escape_markdown(random.choice(style_bank), version=2)
    body_lines = []

    for title, url, desc in results[:max_entries]:
        clean_desc = clean_html(desc or "")
        title_md = escape_markdown(title or "No title", version=2)
        desc_md = escape_markdown(clean_desc or "No description", version=2)
        url_md = escape_url(url or "No URL")  # Manual escape for URL

        entry = f"🔍 *{title_md}*\n{desc_md}\n{url_md}"
        body_lines.append(entry)

    body = "\n\n".join(body_lines)
    full_message = f"{intro}\n\n{body}"

    if len(full_message) > 4000:
        full_message = full_message[:3990] + "\n\n...It was too long, yes precious. We clipped it!"

    print(f"[Search reply length]: {len(full_message)} chars")
    return full_message
