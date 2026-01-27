import streamlit as st
from utils.alsoasked_client import AlsoAskedClient
from utils.gemini_client import get_gemini_variations
from utils.grounding_client import GroundingModel

st.set_page_config(page_title="Candour Keyword Grounding Tool", layout="wide")

st.title("Candour Keyword Grounding Tool")

with st.sidebar:
    st.header("⚙️ Configuration")
    alsoasked_key = st.text_input("AlsoAsked API Key", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    map_conversation = st.checkbox("Map out likely conversation")
    keywords_input = st.text_area("Enter keywords, one per line:")

    if 'persona_count' not in st.session_state:
        st.session_state.persona_count = 0
        st.session_state.personas = [""] * 5

    if st.button("➕ Add Persona") and st.session_state.persona_count < 5:
        st.session_state.persona_count += 1

    for i in range(st.session_state.persona_count):
        st.session_state.personas[i] = st.text_area(f"Persona {i+1}", value=st.session_state.personas[i], key=f"p_{i}")

    start_button = st.button("📊 Start Full Analysis")

if start_button:
    # Ensure this block is indented 1 level (4 spaces)
    keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
    active_personas = [p.strip() for p in st.session_state.personas[:st.session_state.persona_count] if p.strip()] or ["(No Persona Applied)"]

    with st.spinner("Analyzing..."):
        grounding_model = GroundingModel()
        st.session_state.results = {"map_conversation": map_conversation, "combined": [], "conversation_map": []}

        if map_conversation:
            aa_client = AlsoAskedClient(api_key=alsoasked_key)

        for keyword in keywords:
            # This loop is inside the 'with st.spinner' block
            for persona in active_personas:
                # This block is inside the 'for persona' loop
                display_persona = None if persona == "(No Persona Applied)" else persona

                # FIXED: This line must align with 'display_persona' above
                gemini_data = get_gemini_variations(gemini_key, keyword, persona=display_persona)

                gemini_variations = [item["variation"] for item in gemini_data if item["variation"]]
                gemini_search_metadata = [item["web_search_queries"] for item in gemini_data if item["variation"]]

                if gemini_variations:
                    gemini_grounding_scores = grounding_model.analyze_queries(gemini_variations)
                    for i, variation in enumerate(gemini_variations):
                        score = gemini_grounding_scores[i]
                        st.session_state.results["combined"].append({
                            "root_keyword": keyword,
                            "persona": display_persona,
                            "gemini_query": variation,
                            "web_search_queries": gemini_search_metadata[i],
                            "grounding_score": score
                        })

    st.switch_page("pages/1_Results_Dashboard.py")
