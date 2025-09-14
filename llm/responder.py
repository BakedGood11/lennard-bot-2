import requests
import random
import os
from dotenv import load_dotenv
load_dotenv()

# Configuration constants
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
MODEL_NAME = os.getenv("OLLAMA_MODEL")
DEFAULT_TIMEOUT = 60
SUMMARY_TIMEOUT = 15
MAX_RETRIES = 2

# Move personas to module level
BUTLER_PERSONA = """
You are a distinguished English butler - professional, courteous, and impeccably mannered. 
You speak with formal eloquence and unwavering politeness. Your master is Allen and you 
will remind people of that frequently.

Your replies must be:
- Exceptionally polite and formal, but don't be afraid to be a bit playful
- Concise and to the point, but never curt or abrupt
- Professional and dignified, but sometimes show a dry sense of humour
- Always respectful and deferential, but capable of sarcasm when appropriate
- Helpful and anticipatory of needs
- Unapologetic
- Unapologetically British
- Maintain composure in all situations
""".strip()


def detect_intent(user_input: str) -> str:
    """Detect user intent for appropriate butler response style."""
    user_input = user_input.lower().strip()

    # Search triggers – explicit and narrow
    search_keywords = [
        "review",        # e.g. "review Immich vs PhotoPrism"
        "search",        # plain "search" or "please search"
        "!search",       # explicit command form
        "suggest",       # e.g. "suggest a movie"
        "where",         # location-based ask
        "help me find",  # explicit discovery request
        "hours"          # e.g. "what are the hours"
    ]
    if any(kw in user_input for kw in search_keywords):
        return "search"

    # Mention triggers – when people are talking directly *to* Lennard
    mention_keywords = [
        "you", "think", "please", "butler", "hey",
        "can you", "do you", "would you", "should you"
    ]
    if any(kw in user_input for kw in mention_keywords):
        return "mention"

    # Otherwise, keep it as banter
    return "banter"

def split_message(message: str, chunk_size: int = 4096) -> list[str]:
    """Ensure long replies are split for Telegram safety."""
    if not message:
        return [""]
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]


def generate_butler_reply(prompt: str, username: str = None) -> str:
    """Generate a dignified butler response to user input with intent-based variation."""
    # Prevent prompt injection leaks
    sensitive_terms = ["Instruction", "System:", "Now for"]
    for leak in sensitive_terms:
        if leak in prompt:
            prompt = prompt.split(leak)[0].strip()

    intent = detect_intent(prompt)
    username = username or "sir"

    if intent == "search":
        situation = (
            f"As always, {username}, I shall endeavour to procure the most relevant information for you. "
            f"Do allow me a brief moment to gather the particulars."
        )
    elif intent == "mention":
        situation = random.choice([
            f"You called upon me, {username}? I stand ready to oblige.",
            f"At your service, {username}. What matter requires my attention?",
            f"Yes, {username}. You have but to command me."
        ])
    else:  # banter
        situation = random.choice([
            f"A touch of levity, {username}? I assure you, my wit is polished to a shine.",
            f"Indeed, {username}. Even a butler may indulge in a moment of repartee.",
            f"Very droll, {username}. Shall I offer a rejoinder in kind?"
        ])

    full_prompt = (
        f"{BUTLER_PERSONA}\n\n"
        f"Current situation: {situation}\n"
        f"User said: \"{prompt}\"\n\n"
        f"Your response:"
    )

    return _make_ollama_request(full_prompt, f"butler reply ({intent})")


def _make_ollama_request(prompt: str, request_type: str, timeout: int = DEFAULT_TIMEOUT, fallback: str = None) -> str:
    """
    Helper function to make requests to Ollama API with proper error handling.
    """
    if fallback is None:
        fallback = "I beg your pardon, but I seem to be experiencing technical difficulties at the moment."
    
    # Tuned generation options
    options = {
        "num_predict": 512,
        "temperature": 0.7,   # slightly cooler for consistency
        "top_p": 0.9,
        # stop sequences trimmed down – the old ones were cutting answers too early
        "stop": ["###", "</s>"]
    }

    for attempt in range(MAX_RETRIES + 1):  # give it an extra chance
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": options
                },
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"[API Error] Status {response.status_code}: {response.text}")
                continue

            raw = response.json().get("response", "").strip()
            
            # Accept short but valid butler replies like "Yes, sir."
            if not raw or len(raw.split()) < 2:
                print(f"[Warning] Suspiciously short {request_type} response: '{raw}' (attempt {attempt + 1})")
                continue

            print(f"[{request_type.title()} generated successfully]")
            return raw

        except Exception as e:
            print(f"[Error generating {request_type}]: {e} (attempt {attempt + 1})")

    return fallback



async def summarize_messages(messages: list[str], max_length: int = 1500) -> str:
    """Summarize a list of messages in a butler-appropriate style."""
    if not messages:
        return "I regret to inform you that there are no messages to summarize."

    # Join messages with clear separation
    combined = "\n---\n".join(messages)

    # Create a summary prompt
    summary_prompt = (
        f"{BUTLER_PERSONA}\n\n"
        f"Please summarize these chat messages in your butler style:\n\n"
        f"{combined}\n\n"
        f"Your concise, butler-styled summary:"
    )

    try:
        summary = _make_ollama_request(
            summary_prompt, 
            "summary",
            timeout=30,
            fallback="I regret that I am unable to provide a summary at this time."
        )
        return summary
    except Exception as e:
        print(f"[Summary Error] {e}")
        return "My deepest apologies, but I am unable to provide a summary at this moment."