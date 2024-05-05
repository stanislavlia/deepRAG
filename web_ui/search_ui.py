import streamlit as st
import pandas as pd


text_search = st.text_input("Search pages", value="")

df = pd.DataFrame({"Autor" : ["Mark", "Mark", "Mark", "Mark"] * 2,
				    "Title" : ["Title1", "Title2", "Good book", "Bad book"] * 2})


if text_search:
    df_search = df[df["Autor"] == text_search]
    st.write(df_search)


N_cards_per_row = 2
if text_search:
    for n_row, row in df_search.reset_index().iterrows():
        i = n_row%N_cards_per_row
        if i==0:
            st.write("---")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[n_row%N_cards_per_row]:
            st.caption(f"{row['Title'].strip()}")
            st.markdown(f"**{row['Autor'].strip()}**")
            st.markdown("""Customers of BigQuery include 20th Century Fox, American Eagle Outfitters, HSBC, CNA Insurance, 
                    Asahi Group, ATB Financial, Athena, The Home Depot, Wayfair, Carrefour, Oscar Health,
                     and several others.[16] Gartner named Google as a Leader in the 2021 Magic Quadrant™ 
                    for Cloud Database Management Systems.[17] BigQuery is also named a Leader in The 2021 Forrester Wave: 
                        Cloud Data Warehouse.[18] 
                        According to a study by Enterprise Strategy Group,
                     BigQuery saves up to 27% in total cost of ownership over three years compared to other cloud data warehousing solutions.[19]""")
            