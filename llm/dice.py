import re
import random
import logging

# Configuration constants
MIN_DICE_SIDES = 2
MAX_DICE_SIDES = 1000
FORMAL_RESPONSE_CHANCE = 0.6  # 60% formal, 40% friendly butler
WISDOM_ADDITION_CHANCE = 0.15  # 15% chance for additional butler wisdom

logger = logging.getLogger(__name__)


def handle_dice_roll(user_input: str) -> str | None:
    """
    Detects standard 'dX' dice notation and returns a dignified butler-themed result or None.
    
    Supports patterns like: d20, roll d6, 1d8, etc.
    
    Args:
        user_input: The user's message text
        
    Returns:
        str: Butler-styled dice result, or None if no dice pattern found
    """
    # Enhanced pattern matching for various dice notations
    patterns = [
        r'(?:^|\s)d(\d+)(?:\s|$)',        # Standard: d20
        r'(?:^|\s)(\d+)?d(\d+)(?:\s|$)',  # With quantity: 2d6
        r'roll.*?d(\d+)',                 # "roll d20"
        r'dice.*?d(\d+)'                  # "dice d6"
    ]
    
    match = None
    sides = None
    
    for pattern in patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            # Handle both single die (d20) and multiple dice (2d6) patterns
            if len(match.groups()) == 2 and match.group(1):
                # Pattern with quantity (e.g., 2d6) - for now, just use the die size
                sides = int(match.group(2))
            else:
                # Simple pattern (e.g., d20)
                sides = int(match.group(1))
            break
    
    if not match or sides is None:
        return None
    
    try:
        # Validate dice size
        if sides < MIN_DICE_SIDES or sides > MAX_DICE_SIDES:
            return (
                f"I'm terribly sorry, sir, but I must decline to roll such an unconventional die. "
                f"Perhaps a standard die between d{MIN_DICE_SIDES} and d{MAX_DICE_SIDES} would be more appropriate?"
            )
        
        # Generate the roll
        result = random.randint(1, sides)
        
        # Choose butler persona style
        if random.random() < FORMAL_RESPONSE_CHANCE:
            response = _generate_formal_butler_response(sides, result)
        else:
            response = _generate_friendly_butler_response(sides, result)
        
        # Occasionally add butler wisdom about chance and fortune
        if random.random() < WISDOM_ADDITION_CHANCE:
            wisdom = _get_butler_wisdom()
            response += f"\n\n{wisdom}"
        
        logger.info(f"Butler rolled d{sides}: {result}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing dice roll: {e}")
        return "I beg your pardon, sir, but I encountered a difficulty with that roll. Might we try again?"


def _generate_formal_butler_response(sides: int, result: int) -> str:
    """Generate a formal, dignified butler response to dice roll."""
    formal_responses = [
        f"Very good, sir. The d{sides} has yielded a **{result}**. Most satisfactory.",
        f"Indeed, sir. Your d{sides} roll presents a **{result}**. Quite proper, I must say.",
        f"Certainly, sir. The die settles upon **{result}**. A respectable outcome, if I may observe.",
        f"As you requested, sir. The d{sides} produces **{result}**. Entirely within expectations.",
        f"Most assuredly, sir. Your roll of d{sides} results in **{result}**. Quite acceptable indeed."
    ]
    
    # Add outcome-specific formal commentary
    if result == sides:
        formal_responses.extend([
            f"Exceptional! A perfect **{result}** on your d{sides}. Fortune smiles upon you today, sir.",
            f"Outstanding, sir! The maximum result of **{result}**. Most fortuitous indeed."
        ])
    elif result == 1:
        formal_responses.extend([
            f"A humble **{result}** on your d{sides}, sir. Even the smallest steps lead to great journeys.",
            f"The die shows **{result}**, sir. Sometimes modest beginnings yield remarkable ends."
        ])
    
    return random.choice(formal_responses)


def _generate_friendly_butler_response(sides: int, result: int) -> str:
    """Generate a warmer, more personable butler response to dice roll."""
    friendly_responses = [
        f"There we are! Your d{sides} shows **{result}**. Splendid roll, if I do say so myself.",
        f"Ah, very nice! The d{sides} gives us **{result}**. I'm quite pleased with that outcome, sir.",
        f"Excellent! Your die lands on **{result}**. I had a good feeling about that roll.",
        f"Well done! The d{sides} presents **{result}**. A fine result, I must say.",
        f"Marvelous! Your roll yields **{result}**. The odds were certainly in your favor, sir."
    ]
    
    # Add outcome-specific friendly commentary
    if result == sides:
        friendly_responses.extend([
            f"Magnificent! A perfect **{result}**! Your d{sides} couldn't have done better, sir.",
            f"Extraordinary! The highest possible **{result}**! I'm genuinely delighted for you, sir."
        ])
    elif result == 1:
        friendly_responses.extend([
            f"Ah, a **{result}**. Not to worry, sir - even the finest dice have their humble moments.",
            f"The die shows **{result}**, sir. As I always say, it's not the roll but what you do with it that matters."
        ])
    elif result >= sides * 0.75:  # High roll
        friendly_responses.extend([
            f"Quite impressive! A **{result}** on your d{sides}. You do have a way with dice, sir.",
            f"Splendid work! **{result}** is certainly nothing to scoff at, sir."
        ])
    
    return random.choice(friendly_responses)


def _get_butler_wisdom() -> str:
    """Return occasional butler wisdom about fortune and chance, with references to Allen, the bot's master."""
    wisdom_quotes = [
        "As my grandfather used to say, 'Fortune favors the prepared mind,' sir.",
        "I've observed that luck often accompanies those who approach challenges with proper dignity.",
        "In my years of service, I've learned that chance rewards those who maintain their composure.",
        "Might I note that the finest outcomes often arise from the most unexpected circumstances?",
        "Experience has taught me that persistence often trumps fortune, sir.",
        "I find that maintaining one's standards helps weather both good fortune and poor rolls alike.",
        "Master Allen always reminds me that a steady hand and a calm mind are the best companions for any roll.",
        "As Master Allen would say, 'A gentleman never blames the dice, only his preparation.'",
        "It is Allen, my master, who taught me that every roll is an opportunity for grace, regardless of the outcome.",
        "Master Allen insists that true fortune lies not in the roll, but in how one responds to it."
    ]
    
    return random.choice(wisdom_quotes)


def test_dice_roll():
    """Test function for debugging dice roll functionality."""
    test_inputs = [
        "roll d20",
        "d6 please",
        "I need a d100",
        "can you roll 2d8",
        "dice d4",
        "d999",
        "d1001",  # Should trigger error
        "no dice here",  # Should return None
    ]
    
    print("Testing Butler Dice Roll Handler:")
    print("-" * 40)
    
    for test_input in test_inputs:
        result = handle_dice_roll(test_input)
        print(f"Input: '{test_input}'")
        print(f"Result: {result}")
        print("-" * 40)


if __name__ == "__main__":
    test_dice_roll()