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
    
    # Define CSV conversion function
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    # --- SECTION 1: ALSOASKED RESULTS (Original Keyword) ---
    st.subheader("AlsoAsked 'People Also Ask' Questions (Original Keywords)")

    alsoasked_data = []
    # This section is only included if 'alsoasked' data is present (i.e., if AA was run for the original keywords)
    if results.get("alsoasked"):
        for item in results["alsoasked"]:
            for question in item["questions"]:
                alsoasked_data.append({"Original Keyword": item["keyword"], "Generated Question": question})

    if alsoasked_data:
        aa_df = pd.DataFrame(alsoasked_data)
        st.dataframe(aa_df, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Download AlsoAsked Results as CSV",
            data=convert_df_to_csv(aa_df),
            file_name="alsoasked_results.csv",
            mime="text/csv",
        )
    else:
        st.info("No AlsoAsked questions were found (or the feature was not enabled for original keywords).")

    st.divider()

    # --- SECTION 2: GEMINI & GROUNDING RESULTS ---
    st.subheader("Gemini Variations & Grounding Analysis")
    st.markdown("The greater the grounding score, the more likely the keyword will be useful for optimising for AI visibility.")

    combined_flat_data = []
    if results.get("combined"):
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

    # --- SECTION 3: CONVERSATION MAP RESULTS (NEW) ---
    st.subheader("Conversation Map: PAA for Gemini Queries")

    conversation_map_data = []
    if results.get("conversation_map"):
        for item in results["conversation_map"]:
            base_keyword = item['keyword']
            persona = item['persona']
            for map_result in item['map_results']:
                gemini_variation = map_result['gemini_variation']
                for question in map_result['paa_questions']:
                    conversation_map_data.append({
                        "Original Keyword": base_keyword,
                        "Persona": persona,
                        "Gemini Query": gemini_variation,
                        "Next PAA Question": question
                    })

    if conversation_map_data:
        map_df = pd.DataFrame(conversation_map_data)
        st.dataframe(
            map_df,
            column_config={
                "Original Keyword": st.column_config.TextColumn(width="small"),
                "Persona": st.column_config.TextColumn(width="small"),
                "Gemini Query": st.column_config.TextColumn(width="medium"),
                "Next PAA Question": st.column_config.Text
