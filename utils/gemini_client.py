import google.generativeai as genai

def get_gemini_variations(api_key: str, keyword: str) -> list:
    """Generates 5 conversational variations of a keyword using the Gemini API."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Generate exactly 5 possible variations of how the following keyword could be used
        in a conversational query by a user asking a question to an LLM.
        - The variations should be natural-sounding questions or phrases.
        - Do not add any introduction, conclusion, or extra formatting.
        - Return only a numbered list of the 5 variations.
        KEYWORD: "{keyword}"
        """
        response = model.generate_content(prompt)
        variations = response.text.strip().split('\n')
        # Clean up numbering (e.g., "1. ") from the start of each line
        return [line.split('. ', 1)[-1] for line in variations if line]
    except Exception as e:
        return [f"Gemini API Error: {e}"]
