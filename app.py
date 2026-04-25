# pylint: disable=missing-module-docstring
import io

import duckdb
import pandas as pd
import streamlit as st
import ast


con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

#solution_df = duckdb.sql(ANSWER_STR).df()


with st.sidebar:
    theme = st.selectbox(
        "What would you like to review?",
        ("cross_joins", "GroupBy", "window_functions"),
        index=None,
        placeholder="Select a theme...",
    )
    st.write("You selected:", theme)

    exercise = con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}'").df()
    st.write(exercise)

    exercise_name = exercise.loc[0, "exercise_name"]
    with open(f"answers/{exercise_name}.sql", "r") as f:
        answer = f.read()

    solution_df = con.execute(answer).df()

st.header("Enter your code:")
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
    if theme and not exercise.empty:
        exercise_tables = ast.literal_eval(exercise.loc[0, "tables"])
        for table in exercise_tables:
            st.write(f"table: {table}")
            df_table = con.execute(f"SELECT * FROM {table}").df()
            st.dataframe(df_table)
    else:
        st.write("Please select a theme to see the tables.")

with tab3:
    st.write(answer)
