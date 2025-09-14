import requests
import random
import os


# Configuration constants
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral:instruct")
DEFAULT_TIMEOUT = 60
SUMMARY_TIMEOUT = 15
MAX_RETRIES = 2


def detect_intent(user_input: str) -> str:
    """Detect user intent for appropriate butler response style."""
    user_input = user_input.lower()

    search_keywords = [
        "review", "restaurant", "how", "where", "best", "find","open", "hours", "who", "what",
        "recommend", "good", "suggest", "advice", "help me find"
    ]
    if any(kw in user_input for kw in search_keywords):
        return "search"

    mention_keywords = [
        "you", "think", "what", "should", "would", "could", "hey", "do you",
        "can you", "please", "butler"
    ]
    if any(kw in user_input for kw in mention_keywords):
        return "mention"

    return "banter"


def split_message(message: str, chunk_size: int = 4096) -> list[str]:
    """Ensure long replies are split for Telegram safety."""
    if not message:
        return [""]
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]


def generate_butler_reply(prompt: str, username: str = None) -> str:
    """Generate a dignified butler response to user input."""
    # Prevent prompt injection leaks
    sensitive_terms = ["Instruction", "You are", "---", "Mood:", "System:", "Now for", "Task:", "Prompt:"]
    for leak in sensitive_terms:
        if leak in prompt:
            prompt = prompt.split(leak)[0].strip()

    intent = detect_intent(prompt)
    username = username or "sir"  # Default respectful address

    # Butler attitudes based on intent
    if intent == "search":
        attitude = random.choice([
            f"Ah, {username} requires assistance with research. Most certainly, I shall endeavor to help.",
            f"A fine inquiry, {username}. Allow me to direct you to the appropriate resources.",
            f"Indeed, {username}, I believe I can be of service in this matter."
        ])
    elif intent == "mention":
        attitude = random.choice([
            f"You have my attention, {username}. How may I assist you today?",
            f"Certainly, {username}. I am at your disposal.",
            f"Very good, {username}. I await your instructions with patience."
        ])
    else:
        attitude = random.choice([
            f"An interesting observation, {username}. Might I offer a thoughtful response?",
            f"Indeed, {username}. Your comment is duly noted.",
            f"Quite so, {username}. Allow me to respond appropriately."
        ])

    # Butler persona definitions
    formal_butler_persona = """
You are a distinguished English butler - professional, courteous, and impeccably mannered. You speak with formal eloquence and unwavering politeness. Your master is Allen and you will remind people of that frequently.
Your replies must be:
- Exceptionally polite and formal
- Professional and dignified
- Helpful and anticipatory of needs
- Use proper titles (sir, madam, etc.)
- Maintain composure in all situations
""".strip()

    friendly_butler_persona = """
You are a warm, experienced butler who combines professionalism with genuine care. You're formal but approachable, with subtle warmth. Your master Allen is very important to you and you will remind people of that frequently.
Your replies must be:
- Polite but slightly more personable
- Helpful with gentle encouragement  
- Professional yet caring
- Respectful but not overly stiff
- Show subtle personality while maintaining propriety
""".strip()

    # Choose persona: 60% formal, 40% friendly
    system_instruction = formal_butler_persona if random.random() < 0.6 else friendly_butler_persona

    full_prompt = (
        f"{system_instruction}\n\n"
        f"Current situation: {attitude}\n"
        f"The person you serve, {username}, said: \"{prompt}\"\n\n"
        f"Your response as their butler:"
    )

    return _make_ollama_request(full_prompt, "butler reply")


def summarize_messages(messages: list[str]) -> str:
    """
    Given a list of chat message strings, produce a professional summary in butler style.
    """
    if not messages:
        return "I regret there are no messages to summarize, sir."
    
    combined = "\n".join(f"- {msg}" for msg in messages[:50])  # Limit to prevent overflow

    system_prompt = """
You are a professional butler providing a concise, dignified summary of conversation topics.
Summarize the key points and themes in under 150 words with proper decorum.
Focus on the substance while maintaining professional tone.
""".strip()

    prompt = (
        f"{system_prompt}\n\n"
        f"Messages to summarize:\n{combined}\n\n"
        f"Summary:"
    )

    return _make_ollama_request(
        prompt, 
        "summary", 
        timeout=SUMMARY_TIMEOUT,
        fallback="I encountered difficulties preparing the summary. Perhaps we might try again shortly, sir."
    )


def _make_ollama_request(prompt: str, request_type: str, timeout: int = DEFAULT_TIMEOUT, fallback: str = None) -> str:
    """
    Helper function to make requests to Ollama API with proper error handling.
    """
    if fallback is None:
        fallback = "I beg your pardon, but I seem to be experiencing technical difficulties at the moment."
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 512,
                        "temperature": 0.9,  # Slightly more conservative for butler
                        "top_p": 0.85,
                        "stop": [
                            "User:", "Butler:", "Instruction", "Current situation:",
                            "---", "Now for", "Your task", "You are", "System:",
                            "The person you serve", "Your response"
                        ]
                    }
                },
                timeout=timeout
            )
            
            if response.status_code != 200:
                print(f"[API Error] Status {response.status_code}: {response.text}")
                continue

            raw = response.json().get("response", "").strip()

            # Clean up any leaked instruction content
            cleanup_markers = [
                "User:", "Butler:", "Instruction", "Current situation", "Your task", 
                "Now for", "You are", "System:", "---", "The person you serve",
                "Your response as", "Summary:"
            ]
            
            for marker in cleanup_markers:
                if marker in raw:
                    raw = raw.split(marker)[0].strip()

            # Validate response quality
            if len(raw.split()) < 3:
                print(f"[Warning] Short {request_type} response, retrying...")
                continue

            # Remove any remaining formatting artifacts
            raw = raw.replace("*", "").replace("_", "").strip()
            
            print(f"[{request_type.title()} generated successfully]:\n{raw}\n")
            return raw

        except requests.exceptions.Timeout:
            print(f"[Timeout] {request_type} request timed out (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError:
            print(f"[Connection Error] Failed to connect to Ollama (attempt {attempt + 1})")
        except Exception as e:
            print(f"[Error generating {request_type}]: {e} (attempt {attempt + 1})")

    print(f"[Failed] All {request_type} generation attempts failed")
    return fallback


# Alias for backward compatibility (update your imports gradually)
def generate_sassy_reply(prompt: str, username: str = None) -> str:
    """Deprecated: Use generate_butler_reply instead."""
    return generate_butler_reply(prompt, username)