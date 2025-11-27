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
    map_conversation = results.get("map_conversation", False)

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    # --- SINGLE DYNAMIC RESULTS TABLE ---

    if map_conversation:
        # Use conversation_map data structure
        table_data = results.get("conversation_map")
        title = "Conversation Mapping & Grounding Analysis"
        info_text = "Analysis of Gemini-generated queries, expanded by AlsoAsked, with grounding scores applied to the *expanded questions*."

        # Define columns for the Conversation Mapping table
        column_map = {
            "root_keyword": "Original Keyword",
            "persona": "Persona",
            "gemini_query": st.column_config.TextColumn("Gemini Query (Initial Step)", width="medium"),
            "expanded_question": st.column_config.TextColumn("AlsoAsked Expanded Question (Next Step)", width="large"),
            "grounding_score": st.column_config.ProgressColumn(
                "Grounding Score (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        }

    else:
        # Use combined data structure (Simple mode)
        table_data = results.get("combined")
        title = "Gemini Query Variations & Grounding Analysis"
        info_text = "Grounding analysis applied to the Gemini-generated query variations."

        # Define columns for the Simple table
        column_map = {
            "root_keyword": "Original Keyword",
            "persona": "Persona",
            "gemini_query": st.column_config.TextColumn("Generated Query (from Gemini)", width="large"),
            "grounding_score": st.column_config.ProgressColumn(
                "Grounding Score (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        }

    # --- DISPLAY THE TABLE ---
    st.subheader(title)
    st.markdown(f"*{info_text}*")

    if table_data:
        # Normalize data keys to standard display keys
        df = pd.DataFrame(table_data)

        # Drop the intermediate 'data' key if it somehow exists
        if 'data' in df.columns:
            df = df.drop(columns=['data'])

        # Rename columns and configure display
        df.rename(columns={'root_keyword': 'Original Keyword', 'persona': 'Persona', 'gemini_query': 'Generated Query (from Gemini)', 'expanded_question': 'AlsoAsked Expanded Question (Next Step)', 'grounding_score': 'Grounding Score'}, inplace=True)

        # Determine the set of columns to actually display based on the selected mode
        display_columns = list(column_map.keys())

        # Create column configuration dictionary for st.dataframe
        column_config_dict = {
            col_name: config for col_name, config in column_map.items()
            if col_name in display_columns
        }

        st.dataframe(
            df[df.columns.intersection(column_map.keys())].rename(columns={k: v.label if hasattr(v, 'label') else v for k, v in column_map.items()}),
            column_config=column_config_dict,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label=f"📥 Download {title} Results as CSV",
            data=convert_df_to_csv(df),
            file_name="keyword_analysis_results.csv",
            mime="text/csv",
        )

    else:
        st.info("No data was generated for the selected analysis mode.")
