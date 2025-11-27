import streamlit as st
from utils.alsoasked_client import AlsoAskedClient
from utils.gemini_client import get_gemini_variations
from utils.grounding_client import GroundingModel

st.set_page_config(page_title="Candour Keyword Grounding Tool", layout="wide")

st.title("Candour Keyword Grounding Tool")
st.markdown("Enter your API keys and a list of keywords to run a full analysis. This is experimental and will probably break or do something weird. If it does, let Tom know")

# SIDEBAR FOR INPUTS
with st.sidebar:
    st.header("⚙️ Configuration")
    alsoasked_key = st.text_input("AlsoAsked API Key", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")

    # --- NEW OPTION CHECKBOX ---
    st.header("🗺️ Advanced Mapping")
    map_conversation = st.checkbox(
        "Map out likely conversation (Requires AlsoAsked API)",
        help="If checked, the Gemini-generated query variations will be pushed back to the AlsoAsked API to find deeper conversational questions."
    )
    # ---------------------------

    st.header("✍️ Keywords")
    keywords_input = st.text_area(
        "Enter keywords, one per line:",
        height=250,
        placeholder="Content marketing for startups\nHealthy breakfast ideas\nBeginner's guide to Python"
    )

    st.header("🎭 User Personas (Optional)")
    st.markdown("Enter up to 5 user personas to generate targeted query variations.")

    if 'persona_count' not in st.session_state:
        st.session_state.persona_count = 1
        st.session_state.personas = [""] * 5

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.persona_count < 5:
            if st.button("➕ Add Persona"):
                st.session_state.persona_count += 1
    with col2:
        if st.session_state.persona_count > 1:
            if st.button("➖ Remove Persona"):
                st.session_state.persona_count -= 1
                st.session_state.personas[st.session_state.persona_count] = ""

    for i in range(st.session_state.persona_count):
        st.session_state.personas[i] = st.text_input(
            f"Persona {i+1}",
            value=st.session_state.personas[i],
            key=f"persona_input_{i}",
            placeholder="e.g., A busy parent who loves cooking"
        )

    active_personas = [p.strip() for p in st.session_state.personas[:st.session_state.persona_count] if p.strip()]
    if not active_personas:
        active_personas = ["(No Persona Applied)"]

    start_button = st.button("📊 Start Full Analysis")

# MAIN WORKFLOW
if start_button:
    # --- CHECK FOR REQUIRED KEYS ---
    if map_conversation and not alsoasked_key:
         st.error("The 'Map out likely conversation' option requires the AlsoAsked API Key.")
         st.stop()

    if not all([gemini_key, keywords_input]):
        st.warning("Please provide the Gemini API key and at least one keyword.")
        st.stop()
    # -------------------------------

    keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]

    with st.spinner("Running full analysis... This may take a few minutes. Don't navigate to the results dashboard before finishing or it will break and u will be sad"):
        # Initialize clients
        if map_conversation:
             aa_client = AlsoAskedClient(api_key=alsoasked_key)

        grounding_model = GroundingModel()

        # Prepare data storage
        # We now only need to store the data that will be used for the final table.
        # If mapping is off, we use 'combined'. If mapping is on, we use 'conversation_map'.
        st.session_state.results = {
            "map_conversation": map_conversation, # Store the flag
            "combined": [], # Used if map_conversation is False
            "conversation_map": [] # Used if map_conversation is True
        }

        # Main processing loop
        for keyword in keywords:

            for persona in active_personas:

                # 1. Gemini Variations
                if persona == "(No Persona Applied)":
                    display_persona = None
                    gemini_variations = get_gemini_variations(gemini_key, keyword, persona=None)
                else:
                    display_persona = persona
                    gemini_variations = get_gemini_variations(gemini_key, keyword, persona=persona)

                # 2. Grounding Analysis (on Gemini outputs)
                gemini_grounding_scores = grounding_model.analyze_queries(gemini_variations)


                if map_conversation:
                    # 3. Conversation Mapping: Use Gemini output as input for AlsoAsked
                    for i, variation in enumerate(gemini_variations):
                        aa_questions = aa_client.get_questions_for_keyword(variation)

                        # Apply Grounding Analysis to AlsoAsked outputs
                        if aa_questions and not aa_questions[0].startswith("API"): # Check if actual questions were returned
                            aa_grounding_scores = grounding_model.analyze_queries(aa_questions)

                            # Store the expanded results
                            for j, question in enumerate(aa_questions):
                                score = aa_grounding_scores[j] if j < len(aa_grounding_scores) else "Error"
                                st.session_state.results["conversation_map"].append({
                                    "root_keyword": keyword,
                                    "persona": display_persona,
                                    "gemini_query": variation,
                                    "expanded_question": question,
                                    "grounding_score": score
                                })
                        else:
                             # Handle case where AlsoAsked returns an error or no questions
                             st.session_state.results["conversation_map"].append({
                                "root_keyword": keyword,
                                "persona": display_persona,
                                "gemini_query": variation,
                                "expanded_question": "No AlsoAsked questions found or API error.",
                                "grounding_score": "N/A"
                             })


                else:
                    # 3. Simple mode: Only store Gemini/Grounding results
                    for i, variation in enumerate(gemini_variations):
                        score = gemini_grounding_scores[i] if i < len(gemini_grounding_scores) else "Error"
                        st.session_state.results["combined"].append({
                            "root_keyword": keyword,
                            "persona": display_persona,
                            "gemini_query": variation,
                            "grounding_score": score
                        })

    st.success("Analysis complete! Switching to the results dashboard...")
    st.switch_page("pages/1_Results_Dashboard.py")
