import streamlit as st
import pandas as pd
import numpy as np # Import for potential NaN handling

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
    full_column_config = {
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

    if table_data:
        df = pd.DataFrame(table_data)

        # 1. Rename the raw keys to friendly labels (using values from full_column_config)
        # We need the keys of the config to be the columns in the DataFrame for the config to apply
        df.rename(columns={
            'root_keyword': 'root_keyword',
            'persona': 'persona',
            'gemini_query': 'gemini_query',
            'expanded_question': 'expanded_question',
            'grounding_score': 'grounding_score'
        }, inplace=True)

        # 2. Drop the expanded_question column if we are in simple mode
        if not map_conversation and 'expanded_question' in df.columns:
            df.drop(columns=['expanded_question'], inplace=True)

        # 3. Filter the column config to only include columns present in the DataFrame
        display_keys = list(df.columns)
        column_config_dict = {k: v for k, v in full_column_config.items() if k in display_keys}

        # 4. Map the column keys in the DataFrame to the final display labels
        # (This must be done after filtering the config but before passing to st.dataframe)
        df.columns = [full_column_config[col].label if hasattr(full_column_config[col], 'label') else full_column_config[col] for col in df.columns]

        st.dataframe(
            df,
            column_config={v.label if hasattr(v, 'label') else v: full_column_config[k] for k, v in column_config_dict.items()},
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
        st.info("No data was generated for the selected analysis mode. Please ensure you provided keywords and API keys.")
