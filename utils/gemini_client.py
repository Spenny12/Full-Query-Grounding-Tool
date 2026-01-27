from google import genai
from google.genai import types
import re

def get_gemini_variations(api_key: str, keyword: str, persona: str = None) -> list:
    """Generates variations and then probes each one individually for specific grounding search queries."""
    try:
        client = genai.Client(api_key=api_key)

        # PHASE 1: Generate the 5 Variations (No grounding tool needed here)
        persona_instruction = f"The user has the persona: '{persona}'." if persona else ""
        gen_prompt = f"""
        TASK: Generate 5 distinct conversational questions a user might ask an AI about the keyword: "{keyword}".
        {persona_instruction}
        Output ONLY a numbered list (1-5). No intro/outro.
        """

        gen_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=gen_prompt
        )

        # Parse the variations
        lines = gen_response.text.strip().split('\n')
        clean_variations = []
        for line in lines:
            match = re.match(r'^\d+\.\s*(.*)', line.strip())
            if match:
                clean_variations.append(match.group(1))

        final_variations = clean_variations[:5]

        # PHASE 2: Grounding Probe
        # For each variation, we ask Gemini a question to trigger its internal search grounding.
        results = []
        google_search_tool = types.Tool(google_search=types.GoogleSearch())

        for variation in final_variations:
            # We use a neutral prompt to see what search queries the variation itself triggers
            probe_prompt = f"Provide a brief answer to this user query: {variation}"

            probe_response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=probe_prompt,
                config=types.GenerateContentConfig(
                    tools=[google_search_tool]
                )
            )

            # Extract the specific search queries for THIS variation
            specific_queries = []
            if probe_response.candidates and probe_response.candidates[0].grounding_metadata:
                metadata = probe_response.candidates[0].grounding_metadata
                if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                    specific_queries = metadata.web_search_queries

            results.append({
                "variation": variation,
                "web_search_queries": ", ".join(specific_queries) if specific_queries else "None"
            })

        return results
    except Exception as e:
        return [{"variation": f"Gemini Error: {e}", "web_search_queries": "N/A"}]
