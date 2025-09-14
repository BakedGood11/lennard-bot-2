import random
import re
import html
from telegram.helpers import escape_markdown


# Butler-styled search introduction phrases
style_bank = [
    "Allow me to present the results of your inquiry, sir.",
    "I have conducted a thorough search and found the following, if I may.",
    "Your search has yielded several promising results, sir.",
    "I trust these findings will be of service to you.",
    "After careful investigation, I have located these resources for your consideration.",
    "Here are the fruits of my research, presented with my compliments.",
    "I am pleased to report that my search has been fruitful, sir.",
    "With your permission, I shall present the most relevant findings."
]


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities with proper care."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode HTML entities
    return html.unescape(text).strip()


def escape_url(url: str) -> str:
    """Escape characters in URLs that conflict with MarkdownV2."""
    if not url:
        return ""
    return re.sub(r'([_*\[\]()~`>#+=|{}.!-])', r'\\\1', url)


def format_search_response(results: list[tuple[str, str, str]], max_entries: int = 3) -> str:
    try:
        if not results:
            return escape_markdown(
                "I regret to inform you that my search has yielded no results, sir. "
                "Perhaps we might try a different approach?", 
                version=2
            )
        
        # Choose an appropriate butler introduction
        intro = escape_markdown(random.choice(style_bank), version=2)
        
        # Format each search result with extra error checking
        body_lines = []
        for i, (title, url, desc) in enumerate(results[:max_entries], 1):
            try:
                # Clean and prepare content
                clean_desc = clean_html(desc or "")
                clean_title = clean_html(title or "")
                
                # Handle empty fields gracefully
                if not clean_title:
                    clean_title = "Untitled Resource"
                if not clean_desc:
                    clean_desc = "Description not available, sir."
                if not url:
                    continue  # Skip entries without URLs
                
                # Escape for MarkdownV2 with extra care
                title_md = escape_markdown(clean_title, version=2)
                desc_md = escape_markdown(clean_desc, version=2)
                url_md = escape_url(url)
                
                entry = f"*{i}\\. {title_md}*\n{desc_md}\n🔗 {url_md}"
                body_lines.append(entry)
            except Exception as e:
                print(f"[Format Error] Error formatting result {i}: {e}")
                continue
        
        if not body_lines:
            return escape_markdown(
                "I apologize, but I encountered difficulties formatting the search results. "
                "Might I suggest rephrasing your query?",
                version=2
            )
            
        return "{}\n\n{}".format(intro, "\n\n".join(body_lines))
        
    except Exception as e:
        print(f"[Format Error] Major error in format_search_response: {e}")
        return escape_markdown(
            "I deeply regret the inconvenience, but I encountered an error processing the search results.",
            version=2
        )


def format_simple_search_response(results: list[tuple[str, str, str]], max_entries: int = 5) -> str:
    """
    Format search results in a simpler, more compact butler style.
    
    Args:
        results: List of tuples containing (title, url, description)  
        max_entries: Maximum number of results to include
        
    Returns:
        str: Simplified formatted search results
    """
    if not results:
        return "I'm terribly sorry, but I found no results for your query, sir."
    
    intro = "Here are your search results, sir:"
    lines = [intro, ""]
    
    for i, (title, url, desc) in enumerate(results[:max_entries], 1):
        clean_title = clean_html(title or f"Result {i}")
        clean_desc = clean_html(desc or "")
        
        # Simple format without markdown
        line = f"{i}. {clean_title}"
        if clean_desc:
            # Truncate description if too long
            if len(clean_desc) > 100:
                clean_desc = clean_desc[:97] + "..."
            line += f"\n   {clean_desc}"
        
        if url:
            line += f"\n   {url}"
        
        lines.append(line)
    
    return "\n\n".join(lines)


# Alias for backward compatibility
def format_search_response_simple(results, max_entries=3):
    """Backward compatibility alias."""
    return format_simple_search_response(results, max_entries)


if __name__ == "__main__":
    # Test the formatter
    test_results = [
        ("Python Programming Guide", "https://example.com/python", "Learn Python programming with this comprehensive guide covering all the basics and advanced topics."),
        ("Advanced Python Techniques", "https://example.com/advanced", "<p>Master advanced Python concepts including decorators, generators, and more.</p>"),
        ("Python Best Practices", "https://example.com/best", "")
    ]
    
    print("Testing Butler Search Formatter:")
    print("=" * 50)
    
    formatted = format_search_response(test_results)
    print(formatted)
    
    print("\n" + "=" * 50)
    print("Simple format test:")
    
    simple = format_simple_search_response(test_results)
    print(simple)