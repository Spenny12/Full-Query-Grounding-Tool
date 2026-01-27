import streamlit as st
from utils.alsoasked_client import AlsoAskedClient
from utils.gemini_client import get_gemini_variations
from utils.grounding_client import GroundingModel

# ... (Streamlit configuration and sidebar code remain identical to previous versions)

if start_button:
    # ... (Key checks and setup remain identical)

    with st.spinner("Running full analysis with Gemini 2.0..."):
        # Initialize model
        grounding_model = GroundingModel()

        st.session_state.results = {
            "map_conversation": map_conversation,
            "combined": [],
            "conversation_map": []
        }

        for keyword in keywords:
            for persona in active_personas:
                display_persona = None if persona == "(No Persona Applied)" else persona

                # Calls the new get_gemini_variations using google-genai SDK
                gemini_data = get_gemini_variations(gemini_key, keyword, persona=display_persona)

                gemini_variations = [item["variation"] for item in gemini_data]
                gemini_search_metadata = [item["web_search_queries"] for item in gemini_data]

                # ... (Storage logic for results remains identical)

    st.success("Analysis complete!")
    st.switch_page("pages/1_Results_Dashboard.py")
