import streamlit as st
import pandas as pd

st.set_page_config(page_title="Results Dashboard", layout="wide")
st.title("📊 Results Dashboard")

if 'results' not in st.session_state:
    st.warning("No analysis has been run yet.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    results = st.session_state.results
    map_conversation = results.get("map_conversation", False)

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    if map_conversation:
        table_data = results.get("conversation_map")
        title = "Conversation Mapping Analysis"
        info_text = "Includes grounding scores and Gemini's internal web search queries."
    else:
        table_data = results.get("combined")
        title = "Gemini Query Grounding Analysis"
        info_text = "Analysis of Gemini variations and their grounding scores."

    column_config_map = {
        "root_keyword": "Original Keyword",
        "persona": "Persona",
        "gemini_query": st.column_config.TextColumn("Generated Query", width="medium"),
        "web_search_queries": st.column_config.TextColumn("Web Search Queries (Grounding)", width="medium"),
        "expanded_question": st.column_config.TextColumn("AlsoAsked Question", width="large"),
        "grounding_score": st.column_config.ProgressColumn(
            "Grounding Score (%)",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),
    }

    st.subheader(title)
    st.markdown(f"*{info_text}*")

    if table_data:
        df = pd.DataFrame(table_data)

        final_column_config = {k: v for k, v in column_config_map.items() if k in df.columns}

        if not map_conversation and 'expanded_question' in df.columns:
            df.drop(columns=['expanded_question'], inplace=True)

        st.dataframe(df, column_config=final_column_config, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Download CSV",
            data=convert_df_to_csv(df),
            file_name="results.csv",
            mime="text/csv",
        )
