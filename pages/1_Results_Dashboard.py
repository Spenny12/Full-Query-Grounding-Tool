import streamlit as st
import pandas as pd

st.set_page_config(page_title="Results Dashboard", layout="wide")
st.title("📊 Results Dashboard")

# --- Check for results in session state ---
if 'results' not in st.session_state:
    st.warning("No analysis has been run yet. Please go back to the Home page and start an analysis.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    results = st.session_state.results
    
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    # --- SECTION 1: GEMINI & GROUNDING RESULTS ---
    st.subheader("Gemini Variations & Grounding Analysis")
    st.markdown("The greater the grounding score, the more likely the keyword will be useful for optimising for AI visibility.")

    # Flatten the combined results for easier display/download
    combined_flat_data = []
    for keyword_set in results["combined"]:
        keyword = keyword_set['keyword']
        for res in keyword_set['data']:
            score = res['score']
            is_grounded = "Yes" if isinstance(score, float) and score >= 50.0 else "No"

            # Append to the flat list
            combined_flat_data.append({
                "Original Keyword": keyword,
                "Persona": res.get('persona', '(N/A)'),
                "Generated Query (from Gemini)": res['variation'],
                "Needs Grounding?": is_grounded,
                "Grounding Score": score
            })

    if combined_flat_data:
        # Display the full table
        combined_df = pd.DataFrame(combined_flat_data)

        st.dataframe(
            combined_df,
            column_config={
                "Original Keyword": st.column_config.TextColumn(width="small"),
                "Persona": st.column_config.TextColumn(width="medium"),
                "Generated Query (from Gemini)": st.column_config.TextColumn(width="large"),
                "Needs Grounding?": st.column_config.TextColumn(width="small"),
                "Grounding Score": st.column_config.ProgressColumn(
                    "Grounding Score (%)",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="📥 Download Gemini/Grounding Results as CSV",
            data=convert_df_to_csv(combined_df),
            file_name="gemini_grounding_results.csv",
            mime="text/csv",
        )

    else:
        st.info("No Gemini variations were generated.")

    st.divider()

    # --- SECTION 2: CONVERSATION MAPPING RESULTS (NEW) ---
    st.subheader("Conversation Mapping: Gemini Queries Expanded by AlsoAsked")

    conversation_map_data = results.get("conversation_map")

    if conversation_map_data:
        map_df = pd.DataFrame(conversation_map_data)

        st.dataframe(
            map_df,
            column_config={
                "root_keyword": "Original Keyword",
                "gemini_query": st.column_config.TextColumn("Gemini Query (Initial Step)"),
                "expanded_question": st.column_config.TextColumn("AlsoAsked Expanded Question (Next Step)")
            },
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="📥 Download Conversation Map Results as CSV",
            data=convert_df_to_csv(map_df),
            file_name="conversation_map_results.csv",
            mime="text/csv",
        )
    else:
        st.info("The 'Map out likely conversation' option was not selected, or no expanded questions were found.")
