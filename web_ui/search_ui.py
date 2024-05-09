import streamlit as st
import pandas as pd
from client import search_in_collection, parse_search_result


text_search = st.text_input("Search pages", value="")


if text_search:
    
	search_result = search_in_collection(query=text_search,
                                        n_results=8,
                                       collection_name="test")
	search_result = parse_search_result(search_result)

	df_search = pd.DataFrame(search_result)
	st.markdown("Result relevance")
	st.write(df_search[["page", "source", "distance"]])


N_cards_per_row = 1
if text_search:
    st.markdown("#### Search results")
    for n_row, row in df_search.reset_index().iterrows():
        i = n_row%N_cards_per_row
        if i==0:
            st.write("---")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[n_row%N_cards_per_row]:
            st.markdown(f"Source: {row['source'].strip()}")
            st.caption(f"Page {row['page']}")
            st.markdown(row["document".strip()])
        
