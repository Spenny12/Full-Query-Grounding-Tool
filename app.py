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

    # --- NEW CHECKBOX FOR CONDITIONAL ALSOASKED API ---
    map_conversation_enabled = st.checkbox(
        "Map out likely conversation (Requires AlsoAsked API)",
        value=False,
        key="map_conversation_enabled_checkbox"
    )

    alsoasked_key = None
    if map_conversation_enabled:
        alsoasked_key = st.text_input("AlsoAsked API Key", type="password")
    else:
        # Display a disabled input or placeholder when not needed
        st.text_input("AlsoAsked API Key (Optional)", value="", disabled=True, help="Ticking the 'Map out likely conversation' box will enable this field.")
    # ---------------------------------------------------

    gemini_key = st.text_input("Gemini API Key", type="password")

    st.header("✍️ Keywords")
    keywords_input = st.text_area(
        "Enter keywords, one per line:",
        height=250,
        placeholder="Content marketing for startups\nHealthy breakfast ideas\nBeginner's guide to Python"
    )

    st.header("🎭 User Personas (Optional)")
    st.markdown("Enter up to 5 user personas to generate targeted query variations.")

    # Using st.session_state to manage the dynamic list of persona inputs
    if 'persona_count' not in st.session_state:
        st.session_state.persona_count = 1
        st.session_state.personas = [""] * 5 # Initialize a list to hold 5 persona strings

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.persona_count < 5:
            if st.button("➕ Add Persona"):
                st.session_state.persona_count += 1
    with col2:
        if st.session_state.persona_count > 1:
            if st.button("➖ Remove Persona"):
                st.session_state.persona_count -= 1
                st.session_state.personas[st.session_state.persona_count] = "" # Clear the removed persona


    # Display text inputs based on the count
    for i in range(st.session_state.persona_count):
        st.session_state.personas[i] = st.text_input(
            f"Persona {i+1}",
            value=st.session_state.personas[i],
            key=f"persona_input_{i}",
            placeholder="e.g., A busy parent who loves cooking"
        )

    # Filter and clean the active personas
    active_personas = [p.strip() for p in st.session_state.personas[:st.session_state.persona_count] if p.strip()]
    if not active_personas:
        # If no persona is entered, use a default placeholder for the loop
        active_personas = ["(No Persona Applied)"]

    start_button = st.button("📊 Start Full Analysis")

# MAIN WORKFLOW
if start_button:
    # Conditional validation
    validation_ok = True
    if map_conversation_enabled and not alsoasked_key:
        st.warning("Please provide the AlsoAsked API Key or untick the 'Map out likely conversation' option.")
        validation_ok = False

    if not gemini_key or not keywords_input:
        st.warning("Please provide the Gemini API Key and at least one keyword.")
        validation_ok = False

    if validation_ok:
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]

        with st.spinner("Running full analysis... This may take a few minutes. Don't navigate to the results dashboard before finishing or it will break and u will be sad"):
            # Initialize clients
            aa_client = AlsoAskedClient(api_key=alsoasked_key) if map_conversation_enabled else None
            grounding_model = GroundingModel()

            # Prepare data storage
            st.session_state.results = {
                "alsoasked": [], # Used for original keyword PAA (from the previous version)
                "combined": [],
                "conversation_map": [] # NEW: For PAA based on Gemini Variations
            }

            # Main processing loop
            for keyword in keywords:
                # 1. AlsoAsked (Original Keyword PAA - retained from before)
                if aa_client:
                    aa_questions = aa_client.get_questions_for_keyword(keyword)
                    st.session_state.results["alsoasked"].append({"keyword": keyword, "questions": aa_questions})

                # Loop through personas to generate and analyze variations
                for persona in active_personas:
                    # Determine persona context for logging and processing
                    if persona == "(No Persona Applied)":
                        display_persona = None
                        gemini_variations = get_gemini_variations(gemini_key, keyword, persona=None)
                    else:
                        display_persona = persona
                        gemini_variations = get_gemini_variations(gemini_key, keyword, persona=persona)

                    # 2. Grounding Analysis (on Gemini Variations)
                    grounding_scores = grounding_model.analyze_queries(gemini_variations)

                    # Combine Gemini and Grounding results
                    combined_data = []

                    # 3. Conversation Mapping (NEW STEP)
                    if aa_client:
                        conversation_data = {"keyword": keyword, "persona": display_persona, "map_results": []}

                    for i, variation in enumerate(gemini_variations):
                        score = grounding_scores[i] if i < len(grounding_scores) else "Error"
                        combined_data.append({"variation": variation, "score": score, "persona": display_persona})

                        # Run AlsoAsked on the GEMINI VARIATION if mapping is enabled
                        if aa_client:
                            # Use AlsoAskedClient to get questions for the GEMINI VARIATION
                            variation_questions = aa_client.get_questions_for_keyword(variation)
                            conversation_data["map_results"].append({
                                "gemini_variation": variation,
                                "paa_questions": variation_questions
                            })

                    # Append results
                    st.session_state.results["combined"].append({"keyword": keyword, "data": combined_data})
                    if aa_client:
                         st.session_state.results["conversation_map"].append(conversation_data)


        st.success("Analysis complete! Switching to the results dashboard...")
        st.switch_page("pages/1_Results_Dashboard.py")
