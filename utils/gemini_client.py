from google import genai
from google.genai import types

def get_gemini_variations(api_key: str, keyword: str, persona: str = None) -> list:
    """Generates variations using the new Google Gen AI SDK with search grounding."""
    try:
        # Initialize the new unified Client
        client = genai.Client(api_key=api_key)

        # Configure the Google Search tool correctly for the new SDK
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        persona_prefix = f"You are acting as a user with the persona: '{persona}'. " if persona else ""

        prompt = f"""
        {persona_prefix}Generate exactly 5 possible variations of how the following keyword could be used
        in a conversational query by a user asking a question to an LLM.
        - The variations should be natural-sounding questions or phrases.
        - Return only a numbered list of the 5 variations.
        KEYWORD: "{keyword}"
        """

        # Call the API using the new Client structure
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[google_search_tool]
            )
        )

        # Extract search queries from grounding metadata
        search_queries = []
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                search_queries = metadata.web_search_queries

        raw_variations = response.text.strip().split('\n')
        clean_variations = [line.split('. ', 1)[-1] for line in raw_variations if line]

        results = []
        for var in clean_variations:
            results.append({
                "variation": var,
                "web_search_queries": ", ".join(search_queries) if search_queries else "None"
            })

        return results[:5]
    except Exception as e:
        return [{"variation": f"Gemini SDK Error: {e}", "web_search_queries": "N/A"}]
