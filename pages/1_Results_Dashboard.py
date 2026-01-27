# ... (Setup and imports remain the same)

    # --- UPDATE COLUMN CONFIGURATIONS ---
    column_config_map = {
        "root_keyword": "Original Keyword",
        "persona": "Persona",
        "gemini_query": st.column_config.TextColumn("Generated Query (from Gemini)", width="medium"),
        "web_search_queries": st.column_config.TextColumn("Web Search Queries (Grounding)", width="medium"), # New Column
        "expanded_question": st.column_config.TextColumn("AlsoAsked Expanded Question", width="large"),
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

        # 1. Create final column configuration
        final_column_config = {}
        for col_name in df.columns:
            if col_name in column_config_map:
                final_column_config[col_name] = column_config_map[col_name]

        # 2. Drop expanded_question if not in mapping mode
        if not map_conversation and 'expanded_question' in df.columns:
            df.drop(columns=['expanded_question'], inplace=True)
            if 'expanded_question' in final_column_config:
                 del final_column_config['expanded_question']

        # 3. Prepare for download
        df_for_download = df.copy()
        df_for_download.rename(columns={
            k: v.label if hasattr(v, 'label') else v
            for k, v in final_column_config.items() if k in df_for_download.columns
        }, inplace=True)

        # 4. Display
        st.dataframe(
            df,
            column_config=final_column_config,
            use_container_width=True,
            hide_index=True
        )

        # ... (Download button remains same)
