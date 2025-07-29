import requests
import random


def detect_intent(user_input: str) -> str:
    user_input = user_input.lower()

    search_keywords = [
        "review", "restaurant", "how", "where", "best", "find", "open", "hours", "recommend", "good"
    ]
    if any(kw in user_input for kw in search_keywords):
        return "search"

    mention_keywords = [
        "you", "think", "what", "should", "would", "could", "hey", "do you"
    ]
    if any(kw in user_input for kw in mention_keywords):
        return "mention"

    return "banter"


def generate_sassy_reply(prompt, username=None):
    # Prevent prompt injection leaks
    for leak in ["Instruction", "You are", "---", "Mood:", "System:", "Now for"]:
        if leak in prompt:
            prompt = prompt.split(leak)[0].strip()

    intent = detect_intent(prompt)

    # LOTR-flavored attitudes
    if intent == "search":
        attitude = random.choice([
            "We searches for the Precious, but it’s not ours to give, nasty little hobbits!",
            "Ugh, wanting reviews again? Tricksy requests from fragile mortals!",
            "Fine, Precious, we hunts clues, but don’t blame us when it’s nothing but shadows."
        ])
    elif intent == "mention":
        attitude = random.choice([
            f"{username or 'Wayward one'}, you pokes Gollum again, yes you do! What do you wants?",
            "What’s it wants, Precious? Talks to us, but gives nothing in return!",
            "Another creature seeking the Precious’s wisdom? Gollum is amused... and angry!"
        ])
    else:
        attitude = random.choice([
            f"{username or 'Stupid fool'}, your words confuses Gollumsss. Speak proper, you do!",
            "Silence is golden, but your silence is just... more silence! Harumph!",
            "Not a question, not a cry for help, just empty chit-chat. Begone, fool!"
        ])

    # --- Persona definitions for LOTR theme ---
    gollum_persona = """
You are Gollum, a twisted creature obsessed with the Precious. You speak in hissing, broken sentences, alternating between hatred and longing.
Your replies must be:
- In-character (never self-aware)
- Trotty and hissing ('we', 'us', 'precious')
- Full of mistrust, greed, and dark humor
- Alternating cruelty and desperation
""".strip()

    smeagol_persona = """
You are Smeagol, the kinder side of Gollum. You speak softly, eagerly, and with innocent hope for friendship.
Your replies must be:
- In-character (never self-aware)
- Polite and hopeful
- Encouraging and uplifting
- Use gentle and pleading tone
""".strip()

    # Choose persona: 50/50 split
    system_instruction = gollum_persona if random.random() < 0.5 else smeagol_persona

    full_prompt = (
        f"{system_instruction}\n\n"
        f"Gollum is feeling: {attitude}\n"
        f"User: {username or 'Wondrous One'} said: \"{prompt}\"\n\n"
        f"Gollum:"
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral:instruct",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 1.1,
                    "top_p": 0.85,
                    "stop": [
                        "User:", "Gollum:", "Instruction", "Mood:",
                        "---", "Now for", "Your task", "You are"
                    ]
                }
            },
            timeout=15
        )

        raw = response.json().get("response", "").strip()

        # Remove any leaked instructions
        leak_markers = [
            "User:", "Gollum:", "Instruction", "Now respond", "Your task", "Mood:",
            "Now for", "You are", "Precious", "Task:", "---"
        ]
        for marker in leak_markers:
            if marker in raw:
                raw = raw.split(marker)[0].strip()

        # Detect corrupted responses
        if not raw or len(raw.split()) < 3:
            return "Gollum’s tongue stumbles, no words to give. Try again, Precious."

        return raw
    except Exception as e:
        return f"Gollum error: {str(e)}"


def summarize_messages(messages: list[str]) -> str:
    """
    Given a list of chat message strings, produce a dry, sardonic summary in Gollum/Smeagol style.
    """
    combined = "\n".join(f"- {msg}" for msg in messages)

    # LOTR-themed summary prompt
    system_prompt = """
You are Gollum, reviewing the chatter of careless hobbits on their silly messaging ring.
Summarize their prattle in under 150 words.
Do not reveal you read every word.
""".strip()

    prompt = (
        f"{system_prompt}\n\n"
        f"Here are their prattle logs:\n{combined}\n\n"
        f"Summary:"
    )

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral:instruct",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "stop": ["User:", "Gollum:", "Instruction", "Summary:", "---"],
                    "num_gpu": 1,
                    "num_ctx": 4096
                }
            },
            timeout=15
        )
        raw = resp.json().get("response", "").strip()

        if not raw or len(raw.split()) < 3:
            return "The prattle is empty or foolish. No summary possible."

        return raw

    except Exception as e:
        return "Gollum refuses to summarize this drivel. Try again later."
