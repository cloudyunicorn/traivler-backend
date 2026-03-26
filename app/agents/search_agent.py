from app.tools.search_tool import search


def search_agent(destination: str, preferences: list):
    pref_text = " ".join(preferences)
    query = f"best {pref_text} places to visit in {destination}"
    return search(query)