import streamlit as st
import pandas as pd
import numpy as np

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

    # --- DEFINE DATA AND METADATA ---
    if map_conversation:
        table_data = results.get("conversation_map")
        title = "Conversation Mapping & Grounding Analysis"
        info_text = "Analysis of Gemini-generated queries, expanded by AlsoAsked, with grounding scores applied to the **expanded questions**."

    else:
        table_data = results.get("combined")
        title = "Gemini Query Variations & Grounding Analysis"
        info_text = "Grounding analysis applied directly to the Gemini-generated query variations."

    # --- DEFINE ALL POSSIBLE COLUMNS AND CONFIGURATIONS (Unified approach) ---
    # The keys must match the raw column names in the DataFrame (df).
    # The values are the configuration object or a simple string for the display label.
    column_config_map = {
        "root_keyword": "Original Keyword",
        "persona": "Persona",
        "gemini_query": st.column_config.TextColumn("Generated Query (from Gemini)", width="medium"),
        "expanded_question": st.column_config.TextColumn("AlsoAsked Expanded Question (Next Step)", width="large"),
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

    if table_data and table_data[0] is not None:
        df = pd.DataFrame(table_data)

        # 1. Create the final column configuration dictionary
        final_column_config = {}
        for col_name in df.columns:
            if col_name in column_config_map:
                final_column_config[col_name] = column_config_map[col_name]

        # 2. If not mapping conversations, drop the expanded_question column and config
        if not map_conversation and 'expanded_question' in df.columns:
            df.drop(columns=['expanded_question'], inplace=True)
            if 'expanded_question' in final_column_config:
                 del final_column_config['expanded_question']

        # 3. Prepare DataFrame for CSV download (renaming columns to user-friendly labels)
        df_for_download = df.copy()
        # Rename the columns for the CSV output
        df_for_download.rename(columns={
            k: v.label if hasattr(v, 'label') else v
            for k, v in final_column_config.items() if k in df_for_download.columns
        }, inplace=True)

        # 4. Display the table
        st.dataframe(
            df,
            column_config=final_column_config,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label=f"📥 Download {title} Results as CSV",
            data=convert_df_to_csv(df_for_download),
            file_name="keyword_analysis_results.csv",
            mime="text/csv",
        )

    else:
        st.info("No data was generated for the selected analysis mode. Please ensure you provided keywords and API keys.")
