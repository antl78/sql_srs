import pandas as pd
import streamlit as st
import duckdb

st.write("""
# SQL SRS
Spaced Repetition System SQL Practice
""")

option = st.selectbox(
    "What would you like to review?",
    ("Joins", "GroupBy", "Windows Functions"),
    index=None,
    placeholder="Select a theme...",
)

st.write('You selected:', option)

data = {"a": [1, 2, 3], "b": [4, 5, 6]}
df = pd.DataFrame(data)

# Connexion DuckDB en mémoire et enregistrement du DataFrame
con = duckdb.connect()
con.register("df", df)

tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

with tab1:
    st.subheader("Requête SQL sur le DataFrame")
    st.caption("Table disponible : `df` — colonnes : `a`, `b`")

    sql_query = st.text_input("Entrez votre requête SQL", value="SELECT * FROM df")
    st.write(f"Vous avez entré la query suivante : {sql_query}")

    if sql_query:
        try:
            result = con.execute(sql_query).df()
            st.success(f"{len(result)} ligne(s) retournée(s)")
            st.dataframe(result)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")

with tab2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)