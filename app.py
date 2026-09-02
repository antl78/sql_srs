# pylint: disable=missing-module-docstring

import os
import logging
from datetime import date, timedelta

import duckdb
import numpy as np
import pandas as pd
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

REVIEW_INTERVALS = [2, 7, 21]  # jours, du plus court au plus long


def _normalize_value(v):
    """1 et 1.0 doivent être considérés comme égaux : on normalise les
    nombres flottants entiers vers leur écriture entière avant comparaison."""
    if isinstance(v, (float, np.floating)):
        if pd.isna(v):
            return "NaN"
        if float(v).is_integer():
            return str(int(v))
        return repr(round(float(v), 9))
    if v is None:
        return "NaN"
    return str(v)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Rend deux résultats comparables : ordre des colonnes et des lignes
    indifférent, valeurs normalisées pour ignorer les différences de type
    (int vs float, etc.)."""
    df = df[sorted(df.columns)].map(_normalize_value)
    return df.sort_values(by=list(df.columns)).reset_index(drop=True)


def dataframes_match(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """Compare deux résultats de requête : mêmes colonnes et mêmes valeurs,
    peu importe l'ordre des colonnes ou des lignes."""
    if set(df1.columns) != set(df2.columns):
        return False
    return _normalize_df(df1).equals(_normalize_df(df2))


def check_users_solution() -> None:
    """Vérifie la requête de l'utilisateur en comparant son résultat à la
    solution attendue (colonnes + valeurs), et affiche un verdict ✅ / ❌."""
    if not query:
        st.warning("Veuillez entrer une requête SQL.")
        return

    try:
        result = con.execute(query).df()
    except Exception as e:
        st.error(f"Erreur SQL : {e}")
        st.session_state["last_check_correct"] = False
        return

    st.dataframe(result)

    if dataframes_match(result, solution_df):
        st.success("✅ Bonne réponse !")
        st.session_state["last_check_correct"] = True
    else:
        st.error("❌ Ce n'est pas (encore) la bonne réponse.")
        st.session_state["last_check_correct"] = False


with st.sidebar:
    due_count = con.execute(
        "SELECT COUNT(*) FROM memory_state WHERE CAST(last_reviewed AS DATE) <= CURRENT_DATE"
    ).fetchone()[0]
    st.metric("À réviser aujourd'hui", due_count)

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
    # Une correction ne compte que pour l'exercice affiché : on oublie le
    # verdict précédent dès qu'on change d'exercice.
    if st.session_state.get("checked_exercise") != exercise_name:
        st.session_state["last_check_correct"] = None
        st.session_state["checked_exercise"] = exercise_name

    st.subheader(exercise_name.replace("_", " ").capitalize())
    st.write(exercise.loc[0, "statement"])

    st.header("Entrez votre code SQL :")
    query = st.text_area(label="Votre code SQL ici", key="user_input")

    if st.button("Valider"):
        check_users_solution()

    interval_step = int(exercise.loc[0, "interval_step"])

    if st.session_state.get("last_check_correct") is True:
        next_days = REVIEW_INTERVALS[min(interval_step, len(REVIEW_INTERVALS) - 1)]
        if st.button(f"✅ Continuer → prochaine révision dans {next_days} jours"):
            con.execute(
                "UPDATE memory_state SET last_reviewed = ?, interval_step = ? "
                "WHERE exercise_name = ?",
                [
                    str(date.today() + timedelta(days=next_days)),
                    min(interval_step + 1, len(REVIEW_INTERVALS) - 1),
                    exercise_name,
                ],
            )
            st.session_state["last_check_correct"] = None
            st.rerun()
    elif st.session_state.get("last_check_correct") is False:
        if st.button(f"🔁 Revoir dans {REVIEW_INTERVALS[0]} jours"):
            con.execute(
                "UPDATE memory_state SET last_reviewed = ?, interval_step = 0 "
                "WHERE exercise_name = ?",
                [str(date.today() + timedelta(days=REVIEW_INTERVALS[0])), exercise_name],
            )
            st.session_state["last_check_correct"] = None
            st.rerun()

    if st.button("Reset"):
        con.execute(
            "UPDATE memory_state SET last_reviewed = '1970-01-01', interval_step = 0 "
            "WHERE exercise_name = ?",
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
