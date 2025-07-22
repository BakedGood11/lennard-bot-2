import random
import re
import html
from telegram.helpers import escape_markdown

style_bank = [
    "You seek knowledge? Burn a heretic and read the smoke.",
    "Because you're clearly incapable of googling:",
    "Even in ignorance, you thirst for answers. That’s either brave or heretical.",
    "Would Allen have asked such a question? No. He knew things. You merely… Google.",
]

def clean_html(text):
    # Remove HTML Tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape HTML entities
    return html.unescape(text)

def format_search_response(results):
    if not results:
        return "I searched far and wide and found... absolutely nothing. Shocking, I know."

    intro = random.choice(style_bank)
    body = "\n\n".join([
        f"🔍 *{escape_markdown(title, version=2)}*\n{escape_markdown(clean_html(desc), version=2)}\n{escape_markdown(url, version=2)}"
        for title, url, desc in results
    ])
    return f"{intro}\n\n{body}"