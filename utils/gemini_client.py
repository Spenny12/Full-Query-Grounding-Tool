import google.generativeai as genai

def get_gemini_variations(api_key: str, keyword: str, persona: str = None) -> list:
    """Generates variations and returns associated grounding search queries."""
    try:
        genai.configure(api_key=api_key)

        # Initialize model with the google_search tool
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )

        persona_prefix = f"You are acting as a user with the persona: '{persona}'. " if persona else ""

        prompt = f"""
        {persona_prefix}Generate exactly 5 possible variations of how the following keyword could be used
        in a conversational query by a user asking a question to an LLM.
        - The variations should be natural-sounding questions or phrases.
        - Do not add any introduction, conclusion, or extra formatting.
        - Return only a numbered list of the 5 variations.
        KEYWORD: "{keyword}"
        """

        response = model.generate_content(prompt)

        # Extract web search queries from grounding metadata
        search_queries = []
        if hasattr(response.candidates[0], 'grounding_metadata'):
            metadata = response.candidates[0].grounding_metadata
            # webSearchQueries contains the actual queries Gemini executed
            if hasattr(metadata, 'web_search_queries'):
                search_queries = metadata.web_search_queries

        raw_variations = response.text.strip().split('\n')
        # Clean up numbering (e.g., "1. ")
        clean_variations = [line.split('. ', 1)[-1] for line in raw_variations if line]

        # Combine the variation with the search queries used
        results = []
        for var in clean_variations:
            results.append({
                "variation": var,
                "web_search_queries": ", ".join(search_queries) if search_queries else "None"
            })

        return results[:5]
    except Exception as e:
        return [{"variation": f"Gemini API Error: {e}", "web_search_queries": "N/A"}]
