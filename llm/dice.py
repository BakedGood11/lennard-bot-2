# dice.py
import re
import random

def handle_dice_roll(user_input: str) -> str | None:
    match = re.search(r'd(\d+)', user_input.lower())
    if match:
        sides = int(match.group(1))
        if sides < 2 or sides > 1000:
            return "What kind of abominable dice are you conjuring? Stick to d2 to d1000, heretic."

        result = random.randint(1, sides)
        snarky_lines = [
            f"*rolls a d{sides}*... It's a **{result}**. Predictably mediocre.",
            f"A d{sides}, really? Fine. You got a **{result}**. May the Omnissiah mock your fate.",
            f"*sighs mechanically* d{sides} result: **{result}**. Happy now?",
            f"The Machine Spirit rolled a d{sides} and spat out a **{result}**. You're welcome, meatbag.",
        ]
        return random.choice(snarky_lines)
    return None
