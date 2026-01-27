import streamlit as st
from utils.alsoasked_client import AlsoAskedClient
from utils.gemini_client import get_gemini_variations
from utils.grounding_client import GroundingModel

st.set_page_config(page_title="Candour Keyword Grounding Tool", layout="wide")

st.title("Candour Keyword Grounding Tool")
st.markdown("Enter your API keys and a list of keywords to run a full analysis.")

# SIDEBAR FOR INPUTS
with st.sidebar:
    st.header("⚙️ Configuration")
    alsoasked_key = st.text_input("AlsoAsked API Key", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")

    st.header("🗺️ Advanced Mapping")
    map_conversation = st.checkbox(
        "Map out likely conversation (Requires AlsoAsked API)",
        help="If checked, the Gemini-generated query variations will be pushed back to the AlsoAsked API."
    )

    st.header("✍️ Keywords")
    keywords_input = st.text_area(
        "Enter keywords, one per line:",
        height=200,
        placeholder="Content marketing for startups"
    )

    st.header("🎭 User Personas (Optional)")
    if 'persona_count' not in st.session_state:
        st.session_state.persona_count = 0
        st.session_state.personas = [""] * 5

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.persona_count < 5:
            if st.button("➕ Add Persona"):
                st.session_state.persona_count += 1
    with col2:
        if st.session_state.persona_count > 0:
            if st.button("➖ Remove Persona"):
                st.session_state.persona_count -= 1
                st.rerun()

    for i in range(st.session_state.persona_count):
        st.session_state.personas[i] = st.text_area(
            f"Persona {i+1}",
            value=st.session_state.personas[i],
            key=f"persona_input_{i}",
            height=60
        )

    active_personas = [p.strip() for p in st.session_state.personas[:st.session_state.persona_count] if p.strip()]
    if not active_personas:
        active_personas = ["(No Persona Applied)"]

    start_button = st.button("📊 Start Full Analysis")

# MAIN WORKFLOW
if start_button:
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

                # 1. Gemini Variations with Search Metadata
                gemini_data = get_gemini_variations(gemini_key, keyword, persona=display_persona)
                gemini_variations = [item["variation"] for item in gemini_data]
                gemini_search_metadata = [item["web_search_queries"] for item in gemini_data]

                # 2. Grounding Analysis
                gemini_grounding_scores = grounding_model.analyze_queries(gemini_variations)

                if map_conversation:
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
                                    "web_search_queries": gemini_search_metadata[i],
                                    "expanded_question": question,
                                    "grounding_score": score
                                })
                        else:
                             st.session_state.results["conversation_map"].append({
                                "root_keyword": keyword,
                                "persona": display_persona,
                                "gemini_query": variation,
                                "web_search_queries": gemini_search_metadata[i],
                                "expanded_question": "No AlsoAsked questions found.",
                                "grounding_score": "N/A"
                             })
                else:
                    for i, variation in enumerate(gemini_variations):
                        score = gemini_grounding_scores[i] if i < len(gemini_grounding_scores) else "Error"
                        st.session_state.results["combined"].append({
                            "root_keyword": keyword,
                            "persona": display_persona,
                            "gemini_query": variation,
                            "web_search_queries": gemini_search_metadata[i],
                            "grounding_score": score,
                            "expanded_question": "N/A"
                        })

    st.success("Analysis complete!")
    st.switch_page("pages/1_Results_Dashboard.py")
