# pylint: disable=missing-module-docstring
import io
import os
import logging
import duckdb
import pandas as pd
import streamlit as st


if "data" not in os.listdir():
    logging.debug(os.listdir())
    logging.debug("creating folder data")
    os.mkdir("data")

if "exercises_sql_tables.duckdb" not in os.listdir("data"):
    exec(open("init_db.py").read()) # pylint disable
    # subprocess.run(["python", "init_db.py"]) # ne marche pas avec Streamlit

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

with st.sidebar:
    theme = st.selectbox(
        "What would you like to review?",
        ("cross_joins", "GroupBy", "window_functions"),
        index=None,
        placeholder="Select a theme...",
    )
    st.write("You selected:", theme)

    if theme:
        exercise = con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}'").df().sort_values("last_reviewed").reset_index()
        st.write(exercise)

        exercise_name = exercise.loc[0, "exercise_name"]
        with open(f"answers/{exercise_name}.sql", "r") as f:
            answer = f.read()

        solution_df = con.execute(answer).df()

st.header("Enter your code:")

if not theme:
    st.info("Select a theme from the left sidebar")
else:
    query = st.text_area(label="Votre code SQL ici", key="user_input")

    if st.button("Valider"):
        if query:
            try:
                result = con.execute(query).df()
                st.dataframe(result)
            except Exception as e:
                st.error(f"Erreur SQL : {e}")
        else:
            st.warning("Veuillez entrer une requête SQL.")

    tab2, tab3 = st.tabs(["Tables", "Solution"])

    with tab2:
        exercise_tables = exercise.loc[0, "tables"]
        for table in exercise_tables:
            st.write(f"table: {table}")
            df_table = con.execute(f"SELECT * FROM {table}").df()
            st.dataframe(df_table)

    with tab3:
        st.write(answer)