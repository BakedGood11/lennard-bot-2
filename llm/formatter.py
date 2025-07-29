import random
import re
import html
from telegram.helpers import escape_markdown

# LOTR-themed style bank for search intros
style_bank = [
    "We looks for the Precious' whispers through the shadows.",
    "Fragile hobbitses, stumbling in darkness, craving knowledge they cannot grasp.",
    "Even Gollum's precious knows better than to trust hobbitcraft searches.",
    "Would Allen have asked this? No. He wielded wisdom, not mere queries."
]

def clean_html(text: str) -> str:
    """
    Strip away the hobbitish tags and uncurse any entities.
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape HTML entities
    return html.unescape(text)


def format_search_response(results: list[tuple[str, str, str]]) -> str:
    """
    Format Brave search results with a Gollum/Smeagol flair and Markdown escape.
    """
    if not results:
        return "Gollum searched far and wide and found naught. Precious is displeased."

    intro = random.choice(style_bank)

    # Build body: title, description, URL
    body_lines = []
    for title, url, desc in results:
        clean_desc = clean_html(desc)
        title_md = escape_markdown(title, version=2)
        desc_md = escape_markdown(clean_desc, version=2)
        url_md = escape_markdown(url, version=2)
        entry = f"🔍 *{title_md}*\n{desc_md}\n{url_md}"
        body_lines.append(entry)
    body = "\n\n".join(body_lines)

    return f"{intro}\n\n{body}"
