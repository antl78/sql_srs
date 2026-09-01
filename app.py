# pylint: disable=missing-module-docstring

import os
import logging
from datetime import date, timedelta

import duckdb
import streamlit as st


if "data" not in os.listdir():
    logging.debug(os.listdir())
    logging.debug("creating folder data")
    os.mkdir("data")

if "exercises_sql_tables.duckdb" not in os.listdir("data"):
    exec(open("init_db.py").read()) # pylint disable
    # subprocess.run(["python", "init_db.py"]) # ne marche pas avec Streamlit

@st.cache_resource
def get_connection():
    """Connexion DuckDB unique, réutilisée entre les reruns Streamlit."""
    return duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)


con = get_connection()


def check_users_solution() -> None:
    """
    Vérifie si l'utilisateur a entré une bonne requête SQL.
    1 : vérifie les colonnes
    2 : vérifie les valeurs
    """
    global result, e
    if query:
        try:
            result = con.execute(query).df()
            st.dataframe(result)
        except Exception as e:
            st.error(f"Erreur SQL : {e}")
    else:
        st.warning("Veuillez entrer une requête SQL.")


with st.sidebar:
    available_themes_df = con.execute(
        "SELECT DISTINCT theme FROM memory_state ORDER BY theme"
    ).df()
    themes = available_themes_df["theme"].tolist()

    theme = st.radio(
        "Que voulez-vous revoir ?",
        themes,
        index=None,
        key="selected_theme",
    )
    st.write("Vous avez sélectionné :", theme)

    if theme:
        exercise = con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}'").df().sort_values("last_reviewed").reset_index()
        exercise_name = exercise.loc[0, "exercise_name"]
        st.caption(f"Exercice : {exercise_name.replace('_', ' ')}")

        with open(f"answers/{exercise_name}.sql", "r") as f:
            answer = f.read()

        solution_df = con.execute(answer).df()

if not theme:
    st.info("Sélectionnez un thème dans la barre à gauche")
else:
    st.subheader(exercise_name.replace("_", " ").capitalize())
    st.write(exercise.loc[0, "statement"])

    st.header("Entrez votre code SQL :")
    query = st.text_area(label="Votre code SQL ici", key="user_input")

    if st.button("Valider"):
        check_users_solution()

    for n_days in [2, 7, 21]:
        if st.button(f"Revoir dans {n_days} jours"):
            next_review = date.today() + timedelta(days=n_days)
            con.execute(f"UPDATE memory_state SET last_reviewed = '{next_review}' WHERE exercise_name = '{exercise_name}'")
            st.rerun()

    if st.button("Reset"):
        con.execute(
            "UPDATE memory_state SET last_reviewed = '1970-01-01' WHERE exercise_name = ?",
            [exercise_name],
        )
        st.rerun()

    tab2, tab3 = st.tabs(["Tables", "Solution"])

    with tab2:
        exercise_tables = exercise.loc[0, "tables"]
        for table in exercise_tables:
            st.write(f"table: {table}")
            df_table = con.execute(f"SELECT * FROM {table}").df()
            st.dataframe(df_table)

    with tab3:
        st.write(answer)