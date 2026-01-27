# ... (Previous imports and setup remain the same)

# Inside the processing loop:
                gemini_data = get_gemini_variations(gemini_key, keyword, persona=display_persona)

                # Filter out any empty variations to prevent dashboard errors
                gemini_variations = [item["variation"] for item in gemini_data if item["variation"]]
                gemini_search_metadata = [item["web_search_queries"] for item in gemini_data if item["variation"]]

                # Only proceed if variations were successfully generated
                if not gemini_variations:
                    continue

                # Grounding Analysis
                gemini_grounding_scores = grounding_model.analyze_queries(gemini_variations)
# ... (Rest of the loop remains the same)
