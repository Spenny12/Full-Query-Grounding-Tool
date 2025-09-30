import streamlit as st
from utils.alsoasked_client import AlsoAskedClient
from utils.gemini_client import get_gemini_variations
from utils.grounding_client import GroundingModel

st.set_page_config(page_title="Candour Keyword Grounding Tool", layout="wide")

st.title("🚀 Keyword Analysis Suite")
st.markdown("Enter your API keys and a list of keywords to run a full analysis. This is experimental and will probably break or do something weird. If it does, let Tom know")

# SIDEBAR FOR INPUTS
with st.sidebar:
    st.header("⚙️ Configuration")
    alsoasked_key = st.text_input("AlsoAsked API Key", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.header("✍️ Keywords")
    keywords_input = st.text_area(
        "Enter keywords, one per line:",
        height=250,
        placeholder="Content marketing for startups\nHealthy breakfast ideas\nBeginner's guide to Python"
    )
    
    start_button = st.button("📊 Start Full Analysis")

# MAIN WORKFLOW
if start_button:
    if not all([alsoasked_key, gemini_key, keywords_input]):
        st.warning("Please provide all API keys and at least one keyword.")
    else:
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        with st.spinner("Running full analysis... This may take a few minutes. Don't navigate to the results dashboard before finishing or it will break and u will be sad"):
            # Initialize clients
            aa_client = AlsoAskedClient(api_key=alsoasked_key)
            grounding_model = GroundingModel()
            
            # Prepare data storage
            st.session_state.results = {
                "alsoasked": [],
                "combined": []
            }
            
            # Main processing loop
            for keyword in keywords:
                # 1. AlsoAsked
                aa_questions = aa_client.get_questions_for_keyword(keyword)
                st.session_state.results["alsoasked"].append({"keyword": keyword, "questions": aa_questions})
                
                # 2. Gemini Variations
                gemini_variations = get_gemini_variations(gemini_key, keyword)
                
                # 3. Grounding Analysis
                grounding_scores = grounding_model.analyze_queries(gemini_variations)
                
                # Combine Gemini and Grounding results
                combined_data = []
                for i, variation in enumerate(gemini_variations):
                    score = grounding_scores[i] if i < len(grounding_scores) else "Error"
                    combined_data.append({"variation": variation, "score": score})
                
                st.session_state.results["combined"].append({"keyword": keyword, "data": combined_data})

        st.success("Analysis complete! Switching to the results dashboard...")
        st.switch_page("pages/1_Results_Dashboard.py")
