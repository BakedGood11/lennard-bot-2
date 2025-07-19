import os
import requests
from dotenv import load_dotenv

load_dotenv()
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

def search_brave(query, num_results=3):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {"q": query, "count": num_results}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("web", {}).get("results", [])

        if not results:
            print("[Brave API] No results found.")
            return []

        return [
            (
                r.get("title", "No Title"),
                r.get("url", "No URL"),
                r.get("description", "No Description"),
            )
            for r in results
        ]
    except requests.exceptions.RequestException as e:
        print(f"[Brave API] Request error: {e}")
        if 'response' in locals():
            print(f"[Brave API] Response content: {response.text}")
        return []
    except Exception as e:
        print(f"[Brave API] Unexpected error: {e}")
        return []
