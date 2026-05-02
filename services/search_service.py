"""
Internet search service for Arcanum.
Uses DuckDuckGo instant answer API (no key needed) and Wikipedia.
Results are shown in the app UI, NOT in a browser.
"""
import requests
import re


class SearchService:
    DDG_API = "https://api.duckduckgo.com/"
    WIKIPEDIA_API = "https://es.wikipedia.org/api/rest_v1/page/summary/"

    def search(self, query: str) -> str:
        """
        Search for information and return a text answer.
        Tries DuckDuckGo first, then Wikipedia.
        """
        # Try DuckDuckGo instant answer
        result = self._duckduckgo_search(query)
        if result:
            return result

        # Fallback to Wikipedia
        result = self._wikipedia_search(query)
        if result:
            return result

        return f"I couldn't find information about: {query}"

    def _duckduckgo_search(self, query: str) -> str | None:
        """Search using DuckDuckGo instant answer API."""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            }
            response = requests.get(self.DDG_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check for abstract/answer
            if data.get("AbstractText"):
                source = data.get("AbstractSource", "")
                text = data["AbstractText"]
                # Limit length for speech
                if len(text) > 500:
                    text = text[:500] + "..."
                return f"{text} (Source: {source})"

            if data.get("Answer"):
                return data["Answer"]

            # Check related topics
            topics = data.get("RelatedTopics", [])
            if topics and isinstance(topics[0], dict) and topics[0].get("Text"):
                return topics[0]["Text"]

            return None

        except Exception:
            return None

    def _wikipedia_search(self, query: str) -> str | None:
        """Search using Wikipedia summary API (Spanish)."""
        try:
            # Clean query for URL
            clean_query = query.strip().replace(" ", "_")
            url = f"{self.WIKIPEDIA_API}{clean_query}"

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()
            extract = data.get("extract", "")

            if extract:
                if len(extract) > 500:
                    extract = extract[:500] + "..."
                return f"{extract} (Wikipedia)"

            return None

        except Exception:
            return None

    def quick_fact(self, topic: str) -> str:
        """Get a quick fact about a topic."""
        return self.search(topic)
