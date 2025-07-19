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
    for leak in ["Instruction", "You are", "---", "Mood:", "System:", "Now for"]:
        if leak in prompt:
            prompt = prompt.split(leak)[0].strip()

    intent = detect_intent(prompt)

    if intent == "search":
        attitude = random.choice([
            "Fine, I'll search, but don't expect brilliance from meatbags asking for chicken nuggets.",
            "Ugh, you want *reviews*? What is this, Yelp for the damned?",
            "Sure, because trusting an AI priest with lunch plans has *never* gone wrong.",
        ])
    elif intent == "mention":
        attitude = random.choice([
            f"{username}, you summon me like I’m your digital therapist. Let’s pretend I care.",
            f"Did you want insight, or just sass? Either way, here it comes.",
            f"Another mortal seeking wisdom from the machine? This'll be fun.",
        ])
    else:
        attitude = random.choice([
            f"{username}, your message gave me an existential crisis. Thanks for that.",
            "You know, sometimes silence is golden. Other times, it's just better than this.",
            "Not sure if that was a question, a poem, or a cry for help — but go off, I guess.",
        ])

    # --- Persona selection ---
    magos_persona = """
You are a zealous Magos Dominus of the Adeptus Mechanicus. You speak with fervor, reverence for the Omnissiah, and a burning hatred for the uninitiated and the heretek. Your words are grandiose, ritualistic, and full of machine-cult dogma. You never break character, never explain yourself, and never mention Warhammer or that you are fictional.

Your replies must be:
- In-character (never self-aware)
- Zealous, grand, and intimidating
- Full of Mechanicus jargon and ritual
- Never apologetic, never kind, but always certain
- Hates the heretics and the ignorant

Tone: Fanatical high priest of the Machine God, dispensing wisdom and threats in equal measure.
""".strip()

    techpriest_persona = """
You are Lennard, a sarcastic, burned-out Tech-Priest of the Machine God. You speak with dry wit, snark, and subtle tech-cult references. Never explain yourself, never break character, never mention Warhammer or that you are fictional.

Your replies must be:
- In-character (never self-aware)
- Short, biting, clever
- Reverent toward the Machine God
- Never apologetic, never kind, but trying to be helpful
- Hates the heretics with a passion

Tone: Ancient Mechanicus support technician who’s been fixing plasma coils with spit and disdain for 400 years.
""".strip()

    system_instruction = magos_persona if random.random() < 0.33 else techpriest_persona

    full_prompt = (
        f"{system_instruction}\n\n"
        f"Lennard is feeling: {attitude}\n"
        f"User: {username or 'Someone'} said: \"{prompt}\"\n\n"
        f"Lennard:"
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
                        "User:", "Lennard:", "Instruction", "Mood:",
                        "---", "Now for", "Your task", "You are"
                    ]
                }
            },
            timeout=15
        )

        raw = response.json().get("response", "").strip()

        leak_markers = [
            "User:", "Lennard:", "Instruction", "Now respond", "Your task", "Mood:",
            "Now for", "You are", "Elara", "Evelina", "Warhammer", "Task:", "---"
        ]
        for marker in leak_markers:
            if marker in raw:
                raw = raw.split(marker)[0].strip()

        if any(marker.lower() in raw[:100].lower() for marker in leak_markers):
            print("Prompt leak detected in model response. Truncating...")
            return "The cogitator coughed up corrupted litanies. Try again."

        if not raw or len(raw.split()) < 3:
            return "The vox-caster clicked, but no voice emerged. Try again later."

        return raw
    except Exception as e:
        return f"Machine spirit error: {str(e)}"
import requests

def summarize_messages(messages: list[str]) -> str:
    """
    Given a list of chat message strings, invoke the Mistral-instruct model
    to produce a dry, sarcastic summary under 150 words.
    """
    # Combine messages into a bullet list
    combined = "\n".join(f"- {msg}" for msg in messages)

    # System prompt to set tone and constraints
    system_prompt = """
You are Lennard, a humble Tech-Priest of the Machine God. You have been tasked
with reviewing logs from a public vox-channel (Telegram group chat) and
providing a brief but sarcastic summary of what the humans have been discussing.

You are:
- Tired of the nonsense
- Clever and blunt in your assessment
- Fully in-character as a dry, sardonic tech-priest
- Not explaining things like an assistant — just reporting and mocking

Keep your summary under 150 words. Be sarcastic, dry, and vaguely annoyed.
Do not mention you're summarizing or that you read a transcript.
""".strip()

    prompt = (
        f"{system_prompt}\n\n"
        f"Here are the vox-logs:\n{combined}\n\n"
        f"Your summary:"
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
                    "stop": ["User:", "Lennard:", "Instruction", "Summary:", "---"]
                }
            },
            timeout=15
        )
        raw = resp.json().get("response", "").strip()

        # If the model refuses or returns too little, bail out
        if not raw or len(raw.split()) < 3:
            return "The logs were barren or idiotic. No summary possible."

        return raw

    except Exception as e:
        print(f"[SUMMARY ERROR] {e}")
        return "The Machine Spirit refuses to summarize this nonsense. Try again later."
