# ... (Previous imports and setup remain the same)

# MAIN WORKFLOW
if start_button:
    # --- CHECK FOR REQUIRED KEYS ---
    if map_conversation and not alsoasked_key:
         st.error("The 'Map out likely conversation' option requires the AlsoAsked API Key.")
         st.stop()

    if not all([gemini_key, keywords_input]):
        st.warning("Please provide the Gemini API key and at least one keyword.")
        st.stop()

    keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]

    with st.spinner("Running full analysis..."):
        if map_conversation:
             aa_client = AlsoAskedClient(api_key=alsoasked_key)

        grounding_model = GroundingModel()

        st.session_state.results = {
            "map_conversation": map_conversation,
            "combined": [],
            "conversation_map": []
        }

        for keyword in keywords:
            for persona in active_personas:
                display_persona = None if persona == "(No Persona Applied)" else persona

                # 1. Gemini Variations (Now returns list of dicts with search queries)
                gemini_data = get_gemini_variations(gemini_key, keyword, persona=display_persona)

                # Extract text for grounding model and mapping
                gemini_variations = [item["variation"] for item in gemini_data]
                gemini_search_metadata = [item["web_search_queries"] for item in gemini_data]

                # 2. Grounding Analysis (on Gemini outputs)
                gemini_grounding_scores = grounding_model.analyze_queries(gemini_variations)

                if map_conversation:
                    # 3. Conversation Mapping
                    for i, variation in enumerate(gemini_variations):
                        aa_questions = aa_client.get_questions_for_keyword(variation)

                        if aa_questions and not aa_questions[0].startswith("API"):
                            aa_grounding_scores = grounding_model.analyze_queries(aa_questions)

                            for j, question in enumerate(aa_questions):
                                score = aa_grounding_scores[j] if j < len(aa_grounding_scores) else "Error"
                                st.session_state.results["conversation_map"].append({
                                    "root_keyword": keyword,
                                    "persona": display_persona,
                                    "gemini_query": variation,
                                    "web_search_queries": gemini_search_metadata[i], # Added
                                    "expanded_question": question,
                                    "grounding_score": score
                                })
                        else:
                             st.session_state.results["conversation_map"].append({
                                "root_keyword": keyword,
                                "persona": display_persona,
                                "gemini_query": variation,
                                "web_search_queries": gemini_search_metadata[i], # Added
                                "expanded_question": "No AlsoAsked questions found.",
                                "grounding_score": "N/A"
                             })
                else:
                    # 3. Simple mode
                    for i, variation in enumerate(gemini_variations):
                        score = gemini_grounding_scores[i] if i < len(gemini_grounding_scores) else "Error"
                        st.session_state.results["combined"].append({
                            "root_keyword": keyword,
                            "persona": display_persona,
                            "gemini_query": variation,
                            "web_search_queries": gemini_search_metadata[i], # Added
                            "grounding_score": score,
                            "expanded_question": "N/A"
                        })

    st.success("Analysis complete!")
    st.switch_page("pages/1_Results_Dashboard.py")
