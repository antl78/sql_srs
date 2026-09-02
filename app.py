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


def run_check(query_text: str) -> None:
    """Exécute la requête et range le verdict dans session_state, sans
    appeler directement st.write/st.dataframe/... : cette fonction sert
    aussi de callback on_change du text_area (Ctrl+Entrée), et Streamlit
    déconseille d'afficher des éléments depuis un callback."""
    if not query_text:
        st.session_state["check_result"] = {"status": "empty"}
        return

    try:
        result = con.execute(query_text).df()
    except Exception as e:
        st.session_state["check_result"] = {"status": "error", "message": str(e)}
        st.session_state["last_check_correct"] = False
        return

    correct = dataframes_match(result, solution_df)
    st.session_state["check_result"] = {
        "status": "ok",
        "result": result,
        "correct": correct,
    }
    st.session_state["last_check_correct"] = correct


def advance_exercise(name: str, next_days: int, new_step: int) -> None:
    """Callback (on_click) du bouton Continuer : programme la prochaine
    révision. Volontairement PAS de st.rerun() ici — un st.rerun() appelé
    depuis un gestionnaire de bouton a provoqué une perte aléatoire de la
    sélection de thème (session_state vidé) une fois sur deux ; un on_click
    s'exécute avant le script principal, qui repart de toute façon avec les
    données à jour au rerun naturel déclenché par le clic."""
    con.execute(
        "UPDATE memory_state SET last_reviewed = ?, interval_step = ? "
        "WHERE exercise_name = ?",
        [str(date.today() + timedelta(days=next_days)), new_step, name],
    )
    st.session_state["last_check_correct"] = None
    st.session_state["check_result"] = None


def reschedule_exercise(name: str, days: int, step: int = 0) -> None:
    """Callback (on_click) du bouton Revoir plus tard."""
    con.execute(
        "UPDATE memory_state SET last_reviewed = ?, interval_step = ? "
        "WHERE exercise_name = ?",
        [str(date.today() + timedelta(days=days)), step, name],
    )
    st.session_state["last_check_correct"] = None
    st.session_state["check_result"] = None


def reset_exercise_now(name: str) -> None:
    """Callback (on_click) du bouton Reset."""
    con.execute(
        "UPDATE memory_state SET last_reviewed = '1970-01-01', interval_step = 0 "
        "WHERE exercise_name = ?",
        [name],
    )
    st.session_state["last_check_correct"] = None
    st.session_state["check_result"] = None


def scroll_to_top() -> None:
    """Force le retour en haut de la page (utile en changeant d'exercice,
    Streamlit ne le fait pas tout seul après un st.rerun())."""
    st.components.v1.html(
        "<script>"
        "var m = window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if (m) { m.scrollTo(0, 0); }"
        "</script>",
        height=0,
    )


with st.sidebar:
    theme_counts_df = con.execute(
        "SELECT theme, "
        "COUNT(*) FILTER (WHERE CAST(last_reviewed AS DATE) <= CURRENT_DATE) AS due "
        "FROM memory_state GROUP BY theme ORDER BY theme"
    ).df()
    due_by_theme = dict(zip(theme_counts_df["theme"], theme_counts_df["due"].astype(int)))
    st.metric("À réviser aujourd'hui", sum(due_by_theme.values()))

    themes = theme_counts_df["theme"].tolist()

    # Détail par thème affiché à part (et non dans le label des options du
    # radio) : un format_func dont le texte change d'un rerun à l'autre (ici,
    # le nombre à réviser qui diminue au fil des validations) fait perdre à
    # Streamlit la sélection du radio de façon aléatoire — st.session_state
    # ["selected_theme"] se retrouve alors avec le texte affiché au lieu de
    # la valeur choisie. On garde donc des options de radio à texte fixe.
    st.caption(
        " · ".join(f"{t} : {due_by_theme.get(t, 0)} à réviser" for t in themes)
    )

    theme = st.radio(
        "Que voulez-vous revoir ?",
        themes,
        index=None,
        key="selected_theme",
    )

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
    # Un changement d'exercice (nouveau choix de thème, ou passage
    # automatique au suivant du même thème) efface le verdict précédent,
    # vide la zone de texte et remonte en haut de la page.
    if st.session_state.get("checked_exercise") != exercise_name:
        st.session_state["last_check_correct"] = None
        st.session_state["check_result"] = None
        st.session_state["checked_exercise"] = exercise_name
        scroll_to_top()

    st.subheader(exercise_name.replace("_", " ").capitalize())
    st.write(exercise.loc[0, "statement"])

    st.header("Entrez votre code SQL :")
    # La clé dépend de l'exercice : Streamlit traite alors la zone de texte
    # comme un widget neuf à chaque changement d'exercice, donc vide par
    # défaut — plus fiable qu'essayer d'effacer une clé fixe après coup.
    text_key = f"user_input_{exercise_name}"
    query = st.text_area(
        label="Votre code SQL ici (Ctrl+Entrée pour valider)",
        key=text_key,
        on_change=lambda: run_check(st.session_state[text_key]),
    )

    if st.button("Valider", type="primary"):
        run_check(query)

    check_result = st.session_state.get("check_result")
    if check_result:
        if check_result["status"] == "empty":
            st.warning("Veuillez entrer une requête SQL.")
        elif check_result["status"] == "error":
            st.error(f"Erreur SQL : {check_result['message']}")
        elif check_result["status"] == "ok":
            st.dataframe(check_result["result"])
            if check_result["correct"]:
                st.success("✅ Bonne réponse !")
            else:
                st.error("❌ Ce n'est pas (encore) la bonne réponse.")

    interval_step = int(exercise.loc[0, "interval_step"])

    if st.session_state.get("last_check_correct") is True:
        next_days = REVIEW_INTERVALS[min(interval_step, len(REVIEW_INTERVALS) - 1)]
        new_step = min(interval_step + 1, len(REVIEW_INTERVALS) - 1)
        st.button(
            f"✅ Continuer → prochaine révision dans {next_days} jours",
            type="primary",
            on_click=advance_exercise,
            args=(exercise_name, next_days, new_step),
        )
    elif st.session_state.get("last_check_correct") is False:
        st.button(
            f"🔁 Revoir dans {REVIEW_INTERVALS[0]} jours",
            on_click=reschedule_exercise,
            args=(exercise_name, REVIEW_INTERVALS[0], 0),
        )

    st.button(
        "🔄 Remettre à réviser maintenant",
        help=(
            "Repasse cet exercice en tête de file dès aujourd'hui et remet "
            "son intervalle à 2 jours — utile pour le refaire tout de "
            "suite sans attendre son échéance normale."
        ),
        on_click=reset_exercise_now,
        args=(exercise_name,),
    )

    tab2, tab3 = st.tabs(["Tables", "Solution"])

    with tab2:
        exercise_tables = exercise.loc[0, "tables"]
        for table in exercise_tables:
            st.write(f"table: {table}")
            df_table = con.execute(f"SELECT * FROM {table}").df()
            st.dataframe(df_table)

    with tab3:
        st.write(answer)
        st.caption("Résultat de la solution :")
        st.dataframe(solution_df)
