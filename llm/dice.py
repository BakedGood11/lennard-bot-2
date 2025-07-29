import re
import random


def handle_dice_roll(user_input: str) -> str | None:
    """
    Detects standard 'dX' dice notation and returns a Gollum/Smeagol-themed result or None.
    """
    match = re.search(r'd(\d+)', user_input.lower())
    if not match:
        return None

    sides = int(match.group(1))
    # Invalid dice sizes
    if sides < 2 or sides > 1000:
        return (
            "What tricksy dice is this?"
            " Gollum cannot roll such abominations."
            " Stick to d2 through d1000, precious!"
        )

    result = random.randint(1, sides)

    # Choose persona: Gollum or Smeagol
    if random.random() < 0.5:
        # Gollum's cruel commentary
        lines = [
            f"*hisses* The Precious spits out a **{result}**, a miserable roll indeed!",
            f"Gollum tosses d{sides} and it lands on **{result}**. Pathetic, yes, pathetic indeed!",
            f"We hates these dice! But the result is **{result}**, so be it, foolish hobbits!",
        ]
    else:
        # Smeagol's reluctant encouragement
        lines = [
            f"Smeagol hopes it helps... It's a **{result}**, yess precious, a good roll!",
            f"Precious smiles kindly: **{result}**. You did well, preciousss!",
            f"We will protect you, precious. d{sides} gave **{result}**, be brave, yesss!",
        ]

    # Allen-themed twist occasionally
    if random.random() < 0.1:
        lines.append(
            f"Allen, my father, once rolled greater fortunes, but you'll settle for **{result}**, won't you?"
        )

    return random.choice(lines)
