import streamlit as st
from streamlit import session_state as ss

import pandas as pd
from client import search_in_collection, parse_search_result, send_pdf_to_server


text_search = st.text_input("Search pages", value="")


if text_search:
    
	search_result = search_in_collection(query=text_search,
                                        n_results=5,
                                       )
	search_result = parse_search_result(search_result)

	df_search = pd.DataFrame(search_result)

N_cards_per_row = 1
if text_search and len(df_search):
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
        


#UPLOADING PDF ON SIDEBAR
if 'pdf_ref' not in ss:
    ss.pdf_ref = None

# Upload PDF file in the sidebar
uploaded_file = st.sidebar.file_uploader("Upload PDF file", type=('pdf'), key='pdf')

if uploaded_file:
    ss.pdf_ref = uploaded_file

if ss.pdf_ref:
    binary_data = ss.pdf_ref.getvalue()
    send_pdf_to_server(binary_data, uploaded_file.name)
    
    st.sidebar.caption(f"File **{uploaded_file.name}** is uploaded!")



