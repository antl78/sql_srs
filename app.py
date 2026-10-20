# pylint: disable=missing-module-docstring

import itertools
import logging
import os
import random
from collections import Counter, defaultdict
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

# Thèmes d'exercices par niveau de maîtrise SQL (cf. doc du projet), dans
# l'ordre d'affichage de la barre latérale. Un thème absent de ce
# dictionnaire est affiché dans un groupe "Autres", à la fin.
THEME_LEVELS = {
    "Niveau 2 · Joins, CTE, CRUD": [
        "cross_joins", "inner_joins", "left_joins", "outer_join",
        "self_joins", "cte", "crud",
    ],
    "Niveau 3 · Agrégations, CASE WHEN, GROUPING SETS": [
        "aggregation", "case_when", "grouping_sets",
    ],
    "Niveau 4 · Agrégations conditionnelles, dates": [
        "conditional_aggregation", "dates",
    ],
    "Niveau 5 · Window functions": [
        "window_functions", "ranking", "lag_lead",
    ],
}


def _normalize_value(v):
    """1 et 1.0 doivent être considérés comme égaux : on normalise les
    nombres flottants entiers vers leur écriture entière avant comparaison."""
    if v is None or (pd.api.types.is_scalar(v) and pd.isna(v)):
        return "NULL"
    if isinstance(v, (float, np.floating)):
        if float(v).is_integer():
            return str(int(v))
        return repr(round(float(v), 9))
    return str(v)


# Garde-fou : nombre max de permutations testées quand plusieurs colonnes
# ont exactement les mêmes valeurs (cas rare, mais combinatoire).
MAX_COLUMN_PERMUTATIONS = 5000


def dataframes_match(user_df: pd.DataFrame, solution_df: pd.DataFrame) -> bool:
    """Compare deux résultats de requête sur leurs VALEURS uniquement :
    - noms de colonnes ignorés (un alias différent reste une bonne réponse) ;
    - ordre des colonnes et des lignes indifférent ;
    - int vs float (1 vs 1.0) indifférent.

    Les colonnes sont appariées par leur contenu (multiset de valeurs), puis
    les lignes sont comparées en multiset. Si plusieurs colonnes ont le même
    contenu, on essaie les appariements possibles entre elles."""
    if user_df.shape != solution_df.shape:
        return False

    # Colonnes renommées en positions : évite les soucis de noms dupliqués
    # (ex : SELECT * avec JOIN ... ON qui renvoie order_id et order_id_1).
    user = user_df.map(_normalize_value)
    solution = solution_df.map(_normalize_value)
    user.columns = range(user.shape[1])
    solution.columns = range(solution.shape[1])

    def signature(col: pd.Series) -> tuple:
        return tuple(sorted(col))

    user_groups: dict = defaultdict(list)
    for c in user.columns:
        user_groups[signature(user[c])].append(c)
    solution_groups: dict = defaultdict(list)
    for c in solution.columns:
        solution_groups[signature(solution[c])].append(c)

    if {k: len(v) for k, v in user_groups.items()} != {
        k: len(v) for k, v in solution_groups.items()
    }:
        return False

    solution_rows = Counter(map(tuple, solution.to_numpy().tolist()))
    sigs = list(solution_groups)
    candidate_orders = itertools.product(
        *(itertools.permutations(user_groups[s]) for s in sigs)
    )
    for combo in itertools.islice(candidate_orders, MAX_COLUMN_PERMUTATIONS):
        mapping = {}
        for s, user_cols in zip(sigs, combo):
            mapping.update(zip(solution_groups[s], user_cols))
        reordered = user[[mapping[c] for c in solution.columns]]
        if Counter(map(tuple, reordered.to_numpy().tolist())) == solution_rows:
            return True
    return False


# Instructions acceptées pour les exercices du thème "crud".
DML_STATEMENT_TYPES = {
    duckdb.StatementType.INSERT,
    duckdb.StatementType.UPDATE,
    duckdb.StatementType.DELETE,
}


def run_dml_in_sandbox(query_text: str, check_table: str) -> pd.DataFrame:
    """Exécute des INSERT/UPDATE/DELETE dans une transaction, lit l'état de
    check_table, puis annule tout (ROLLBACK) : la base n'est jamais modifiée,
    un exercice CRUD peut donc être refait à l'identique.

    con.cursor() ouvre une connexion séparée sur la même base, avec sa
    propre transaction : la connexion partagée (cache_resource) et les
    autres sessions ne voient jamais les modifications en cours."""
    cursor = con.cursor()
    try:
        cursor.begin()
        cursor.execute(query_text)
        # check_table vient de memory_state (jamais de la saisie
        # utilisateur) ; on le quote quand même comme identifiant.
        quoted_table = '"' + check_table.replace('"', '""') + '"'
        return cursor.execute(f"SELECT * FROM {quoted_table}").df()
    finally:
        cursor.rollback()
        cursor.close()


def run_check(
    text_key: str, solution_df: pd.DataFrame, check_table: str | None = None
) -> None:
    """Exécute la requête et range le verdict dans session_state, sans
    appeler directement st.write/st.dataframe/... : cette fonction sert
    de callback (Ctrl+Entrée et bouton Valider), et Streamlit déconseille
    d'afficher des éléments depuis un callback.

    check_table renseigné = exercice CRUD : la requête est exécutée en
    bac à sable (run_dml_in_sandbox) et c'est l'état final de cette table
    qui est comparé à la solution."""
    query_text = st.session_state.get(text_key, "")
    if not query_text.strip():
        st.session_state["check_result"] = {"status": "empty"}
        return

    try:
        statements = con.extract_statements(query_text)
        if check_table:
            # Exercice CRUD : une ou plusieurs instructions INSERT / UPDATE /
            # DELETE (CTE autorisées), rien d'autre (pas de DROP, CREATE,
            # BEGIN/COMMIT...).
            if not statements or any(
                s.type not in DML_STATEMENT_TYPES for s in statements
            ):
                st.session_state["check_result"] = {
                    "status": "error",
                    "message": "Exercice CRUD : seules des instructions INSERT, "
                    "UPDATE ou DELETE sont acceptées.",
                }
                st.session_state["last_check_correct"] = False
                return
            result = run_dml_in_sandbox(query_text, check_table)
        else:
            # La connexion est en lecture/écriture (progression de
            # révision) : on n'accepte qu'UNE instruction de type SELECT
            # (CTE incluses), sinon un DROP/DELETE/UPDATE tapé dans la zone
            # de texte modifierait réellement la base.
            if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
                st.session_state["check_result"] = {
                    "status": "error",
                    "message": "Seule une requête SELECT (une seule instruction, "
                    "CTE autorisées) est acceptée.",
                }
                st.session_state["last_check_correct"] = False
                return
            result = con.execute(query_text).df()
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.session_state["check_result"] = {"status": "error", "message": str(e)}
        st.session_state["last_check_correct"] = False
        return

    correct = dataframes_match(result, solution_df)
    renamed = correct and sorted(map(str, result.columns)) != sorted(
        map(str, solution_df.columns)
    )
    st.session_state["check_result"] = {
        "status": "ok",
        "result": result,
        "correct": correct,
        "renamed": renamed,
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


def select_theme(theme_name: str) -> None:
    """Callback (on_click) d'un bouton de thème dans la barre latérale."""
    st.session_state["selected_theme"] = theme_name


def reveal_flashcard_answer() -> None:
    """Callback (on_click) du bouton Afficher la réponse."""
    st.session_state["flashcard_revealed"] = True


def next_flashcard(card_names: list) -> None:
    """Callback (on_click) du bouton Carte suivante : tire une nouvelle
    carte au hasard (différente de la précédente s'il y en a plusieurs) et
    masque la réponse."""
    previous = st.session_state.get("flashcard_current")
    choices = [c for c in card_names if c != previous] or card_names
    st.session_state["flashcard_current"] = random.choice(choices)
    st.session_state["flashcard_revealed"] = False


with st.sidebar:
    app_mode = st.radio(
        "Mode",
        ["Exercices SQL", "Mémocards"],
        key="app_mode",
    )
    st.divider()

if app_mode == "Exercices SQL":
    with st.sidebar:
        theme_counts_df = con.execute(
            "SELECT theme, "
            "COUNT(*) FILTER (WHERE CAST(last_reviewed AS DATE) <= CURRENT_DATE) AS due "
            "FROM memory_state GROUP BY theme ORDER BY theme"
        ).df()
        due_by_theme = dict(zip(theme_counts_df["theme"], theme_counts_df["due"].astype(int)))
        st.metric("À réviser aujourd'hui", sum(due_by_theme.values()))

        # Thèmes regroupés par niveau (ordre pédagogique). Un st.radio ne
        # permet pas d'insérer des séparateurs entre ses options : chaque
        # thème est donc un bouton, et le thème choisi est gardé dans
        # session_state (clé non liée à un widget). Le compteur "à réviser"
        # peut figurer dans le label : contrairement au format_func d'un
        # radio, un label de bouton n'a pas de valeur persistée à perdre.
        db_themes = theme_counts_df["theme"].tolist()
        grouped_themes = [
            (level, [t for t in level_themes if t in db_themes])
            for level, level_themes in THEME_LEVELS.items()
        ]
        known_themes = {t for _, level_themes in grouped_themes for t in level_themes}
        other_themes = [t for t in db_themes if t not in known_themes]
        if other_themes:
            grouped_themes.append(("Autres", other_themes))

        st.markdown("**Que voulez-vous revoir ?**")
        for level, level_themes in grouped_themes:
            if not level_themes:
                continue
            st.divider()
            st.caption(level)
            for t in level_themes:
                due = due_by_theme.get(t, 0)
                label = t.replace("_", " ").title()
                st.button(
                    f"{label} ({due})" if due else label,
                    key=f"theme_button_{t}",
                    type="primary"
                    if st.session_state.get("selected_theme") == t
                    else "tertiary",
                    width="stretch",
                    on_click=select_theme,
                    args=(t,),
                )

        theme = st.session_state.get("selected_theme")
        if theme not in db_themes:
            theme = None

        if theme:
            exercise = (
                con.execute("SELECT * FROM memory_state WHERE theme = ?", [theme])
                .df()
                .sort_values("last_reviewed")
                .reset_index(drop=True)
            )
            exercise_name = exercise.loc[0, "exercise_name"]
            st.caption(f"Exercice : {exercise_name.replace('_', ' ').title()}")

            with open(f"answers/{exercise_name}.sql", "r", encoding="utf-8") as f:
                answer = f.read()

            # Thème "crud" : la première table de l'exercice est celle dont
            # l'état final (après la requête) est comparé.
            check_table = (
                str(exercise.loc[0, "tables"][0]) if theme == "crud" else None
            )
            if check_table:
                solution_df = run_dml_in_sandbox(answer, check_table)
            else:
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

        st.subheader(exercise_name.replace("_", " ").title())
        st.write(exercise.loc[0, "statement"])

        st.header("Entrez votre code SQL :")
        # La clé dépend de l'exercice : Streamlit traite alors la zone de texte
        # comme un widget neuf à chaque changement d'exercice, donc vide par
        # défaut — plus fiable qu'essayer d'effacer une clé fixe après coup.
        text_key = f"user_input_{exercise_name}"
        st.text_area(
            label="Votre code SQL ici (Ctrl+Entrée pour valider)",
            key=text_key,
            on_change=run_check,
            args=(text_key, solution_df, check_table),
        )

        st.button(
            "Valider",
            type="primary",
            on_click=run_check,
            args=(text_key, solution_df, check_table),
        )

        check_result = st.session_state.get("check_result")
        if check_result:
            if check_result["status"] == "empty":
                st.warning("Veuillez entrer une requête SQL.")
            elif check_result["status"] == "error":
                st.error(f"Erreur SQL : {check_result['message']}")
            elif check_result["status"] == "ok":
                if check_table:
                    st.caption(
                        f"Table {check_table} après votre requête (modifications "
                        "annulées ensuite, la base n'est pas changée) :"
                    )
                st.dataframe(check_result["result"])
                if check_result["correct"]:
                    st.success("✅ Bonne réponse !")
                    if check_result.get("renamed"):
                        st.caption(
                            "ℹ️ Les noms de colonnes diffèrent de la solution "
                            "(alias) — accepté, seules les valeurs comptent."
                        )
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
            st.code(answer, language="sql")
            st.caption(
                f"Table {check_table} après la solution :"
                if check_table
                else "Résultat de la solution :"
            )
            st.dataframe(solution_df)

else:
    # Mode Mémocards : question/réponse simple pour mémoriser la syntaxe SQL,
    # pas encore branché sur la répétition espacée (REVIEW_INTERVALS) —
    # volontairement minimal pour l'instant, le temps de voir si le contenu
    # et le format conviennent.
    with st.sidebar:
        flashcard_themes = con.execute(
            "SELECT DISTINCT theme FROM flashcards ORDER BY theme"
        ).df()["theme"].tolist()

        flashcard_theme = st.radio(
            "Thème à réviser ?",
            flashcard_themes,
            index=0 if flashcard_themes else None,
            key="selected_flashcard_theme",
        )

    if not flashcard_theme:
        st.info("Aucune mémocard disponible pour l'instant.")
    else:
        flashcards_df = con.execute(
            "SELECT * FROM flashcards WHERE theme = ? ORDER BY card_name",
            [flashcard_theme],
        ).df()

        card_names = list(flashcards_df["card_name"])

        # Changement de thème (ou premier passage) : tirage initial au
        # hasard, mémorisé dans session_state pour rester stable entre les
        # reruns tant qu'on reste sur la même carte.
        if st.session_state.get("flashcard_theme_loaded") != flashcard_theme:
            st.session_state["flashcard_current"] = random.choice(card_names)
            st.session_state["flashcard_revealed"] = False
            st.session_state["flashcard_theme_loaded"] = flashcard_theme

        card = flashcards_df[
            flashcards_df["card_name"] == st.session_state["flashcard_current"]
        ].iloc[0]

        nb_cards = len(card_names)
        st.subheader(f"Mémocard — {flashcard_theme} ({nb_cards} carte{'s' if nb_cards > 1 else ''})")
        st.write(card["question"])

        if st.session_state.get("flashcard_revealed"):
            st.success(card["answer"])
            if card["example"]:
                st.code(card["example"], language="sql")
        else:
            st.button("Afficher la réponse", on_click=reveal_flashcard_answer)

        st.button("Carte suivante ➡️", on_click=next_flashcard, args=(card_names,))
