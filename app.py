# pylint: disable=missing-module-docstring

import os
import logging
import duckdb
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
    available_themes_df = con.execute("SELECT DISTINCT theme FROM memory_state").df()
    theme = st.selectbox(
        "Que voulez-vous revoir ?",
        ("cross_joins", "GroupBy", "window_functions"),
        index=None,
        placeholder="Sélectionnez un thème...",
    )
    st.write("Vous avez sélectionné :", theme)

    if theme:
        exercise = con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}'").df().sort_values("last_reviewed").reset_index()
        st.write(exercise)

        exercise_name = exercise.loc[0, "exercise_name"]
        with open(f"answers/{exercise_name}.sql", "r") as f:
            answer = f.read()

        solution_df = con.execute(answer).df()

st.header("Entrez votre code SQL :")

if not theme:
    st.info("Sélectionnez un thème dans la barre à gauche")
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