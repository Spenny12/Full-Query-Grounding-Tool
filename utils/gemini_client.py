from google import genai
from google.genai import types
import re

def get_gemini_variations(api_key: str, keyword: str, persona: str = None) -> list:
    """Generates variations using a stricter prompt and improved parsing."""
    try:
        client = genai.Client(api_key=api_key)

        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Refined prompt to strictly enforce user-query generation
        persona_instruction = f"The user asking these questions has the persona: '{persona}'." if persona else ""

        prompt = f"""
        TASK: Generate exactly 5 distinct examples of how a person would phrase a search or a question to an AI model using the keyword provided below.

        {persona_instruction}

        STRICT RULES:
        - Output ONLY a numbered list (1-5).
        - Do NOT include any introductory text, pleasantries, or conclusions.
        - Each variation must be a natural, conversational query.
        - Format:
          1. [Query 1]
          2. [Query 2]
          ...etc.

        KEYWORD: "{keyword}"
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                temperature=0.7 # Slight randomness for better variety
            )
        )

        search_queries = []
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                search_queries = metadata.web_search_queries

        # Improved Parsing: Only keep lines that start with a digit followed by a period
        lines = response.text.strip().split('\n')
        clean_variations = []
        for line in lines:
            match = re.match(r'^\d+\.\s*(.*)', line.strip())
            if match:
                clean_variations.append(match.group(1))

        # Ensure we have exactly 5 or handle unexpected counts
        final_variations = clean_variations[:5]

        results = []
        for var in final_variations:
            results.append({
                "variation": var,
                "web_search_queries": ", ".join(search_queries) if search_queries else "None"
            })

        return results
    except Exception as e:
        return [{"variation": f"Gemini SDK Error: {e}", "web_search_queries": "N/A"}]
