import random
from telegram.helpers import escape_markdown

style_bank = [
    "Ahem. Not that you'd understand, but here's what I found:",
    "Because you're clearly incapable of googling:",
    "Behold, mortal, the results of your lazy inquiry:",
    "Ugh. Another question. Here's your answer, fleshling:",
]

def format_search_response(results):
    if not results:
        return "I searched far and wide and found... absolutely nothing. Shocking, I know."

    intro = random.choice(style_bank)
    body = "\n\n".join([
        f"🔍 *{escape_markdown(title, version=2)}*\n{escape_markdown(desc, version=2)}\n{escape_markdown(url, version=2)}"
        for title, url, desc in results
    ])
    return f"{intro}\n\n{body}"