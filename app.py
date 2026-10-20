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

CONTENT_DB = "data/exercises_sql_tables.duckdb"
PROGRESS_DB = "data/progress.duckdb"

# Colonnes de progression stockées dans la base de contenu avant la
# séparation contenu / progression (cf. migrate_legacy_progress).
LEGACY_PROGRESS_COLUMNS = ("last_reviewed", "interval_step")


def has_column(connection: duckdb.DuckDBPyConnection, table: str, column: str) -> bool:
    """True si la table de la base de contenu possède cette colonne."""
    return connection.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_catalog = current_database() "
        "AND table_name = ? AND column_name = ?",
        [table, column],
    ).fetchone()[0] > 0


def migrate_legacy_progress(connection: duckdb.DuckDBPyConnection) -> None:
    """Migration unique d'une base créée avant la séparation contenu /
    progression : renomme memory_state en exercises, copie la progression
    existante vers progress.duckdb, puis retire les colonnes de progression
    de la base de contenu. Idempotente : ne fait rien sur une base à jour."""
    content_tables = {
        row[0]
        for row in connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_catalog = current_database()"
        ).fetchall()
    }
    if "memory_state" in content_tables and "exercises" not in content_tables:
        connection.execute("ALTER TABLE memory_state RENAME TO exercises")

    if has_column(connection, "exercises", "last_reviewed"):
        # Seuls les exercices déjà révisés sont copiés : les dates par
        # défaut (1970 / 1980) signifiaient "jamais révisé", ce qui
        # correspond désormais à l'absence de ligne dans exercise_progress.
        connection.execute("""
            INSERT INTO progress.exercise_progress
            SELECT exercise_name, CAST(last_reviewed AS DATE), interval_step
            FROM exercises
            WHERE CAST(last_reviewed AS DATE) > DATE '1980-01-01'
            ON CONFLICT DO NOTHING
        """)

    # Noms de colonnes constants (jamais issus d'une saisie utilisateur).
    for table in ("exercises", "flashcards"):
        for column in LEGACY_PROGRESS_COLUMNS:
            connection.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {column}")


@st.cache_resource
def get_connection():
    """Connexion DuckDB unique, réutilisée entre les reruns Streamlit.

    Deux bases distinctes :
    - CONTENT_DB : exercices, tables d'exercices et mémocards. Versionnée dans
      le repo, régénérable par init_db.py ; l'app n'y écrit jamais (le bac à
      sable CRUD est annulé par ROLLBACK).
    - PROGRESS_DB : progression de révision, locale et ignorée par git,
      attachée sous le nom "progress" (créée au premier lancement)."""
    connection = duckdb.connect(database=CONTENT_DB, read_only=False)
    # Chemin constant : ATTACH n'accepte pas de paramètre préparé.
    connection.execute(f"ATTACH '{PROGRESS_DB}' AS progress")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS progress.exercise_progress (
            exercise_name VARCHAR PRIMARY KEY,
            last_reviewed DATE NOT NULL,
            interval_step INTEGER NOT NULL
        )
    """)
    migrate_legacy_progress(connection)
    return connection


con = get_connection()

REVIEW_INTERVALS = [2, 7, 21]  # jours, du plus court au plus long

# Exercices + état de révision. Un exercice sans ligne dans
# exercise_progress n'a jamais été révisé : il est dû immédiatement.
# position (rowid) départage les ex aequo dans l'ordre du programme.
EXERCISE_STATE_CTE = """
WITH exercise_state AS (
    SELECT
        e.*,
        e.rowid AS position,
        COALESCE(p.last_reviewed, DATE '1970-01-01') AS last_reviewed,
        COALESCE(p.interval_step, 0) AS interval_step
    FROM exercises AS e
    LEFT JOIN progress.exercise_progress AS p USING (exercise_name)
)
"""

# Thèmes par niveau de maîtrise SQL (cf. doc du projet), dans l'ordre
# d'affichage de la barre latérale. Un thème absent de ces dictionnaires
# est affiché dans un groupe "Autres", à la fin.
EXERCISE_THEME_LEVELS = {
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

FLASHCARD_THEME_LEVELS = {
    "Niveau 1 · Fondamentaux": ["null_filtering", "strings", "sets"],
    "Niveau 2 · Joins, CTE, CRUD": ["joins", "cte", "crud"],
    "Niveau 3 · Agrégations, CASE WHEN, GROUPING SETS": [
        "aggregates", "stats", "case_when", "grouping_sets",
    ],
    "Niveau 4 · Agrégations conditionnelles, dates": [
        "conditional_aggregation", "dates",
    ],
    "Niveau 5 · Window functions": ["window_functions"],
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
        # check_table vient de exercises (jamais de la saisie
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
            # La connexion est en lecture/écriture (bac à sable CRUD,
            # base de progression attachée) : on n'accepte qu'UNE
            # instruction de type SELECT
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


def save_progress(name: str, days_from_today: int, interval_step: int) -> None:
    """Programme la prochaine révision d'un exercice (upsert dans la base
    de progression)."""
    con.execute(
        "INSERT INTO progress.exercise_progress VALUES (?, ?, ?) "
        "ON CONFLICT (exercise_name) DO UPDATE SET "
        "last_reviewed = excluded.last_reviewed, "
        "interval_step = excluded.interval_step",
        [name, date.today() + timedelta(days=days_from_today), interval_step],
    )


def advance_exercise(name: str, next_days: int, new_step: int) -> None:
    """Callback (on_click) du bouton Continuer : programme la prochaine
    révision. Volontairement PAS de st.rerun() ici — un st.rerun() appelé
    depuis un gestionnaire de bouton a provoqué une perte aléatoire de la
    sélection de thème (session_state vidé) une fois sur deux ; un on_click
    s'exécute avant le script principal, qui repart de toute façon avec les
    données à jour au rerun naturel déclenché par le clic."""
    save_progress(name, next_days, new_step)
    st.session_state["last_check_correct"] = None
    st.session_state["check_result"] = None


def reschedule_exercise(name: str, days: int, step: int = 0) -> None:
    """Callback (on_click) du bouton Revoir plus tard."""
    save_progress(name, days, step)
    st.session_state["last_check_correct"] = None
    st.session_state["check_result"] = None


def reset_exercise_now(name: str) -> None:
    """Callback (on_click) du bouton Reset : sans ligne de progression,
    l'exercice redevient "jamais révisé", donc dû immédiatement."""
    con.execute(
        "DELETE FROM progress.exercise_progress WHERE exercise_name = ?",
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


def select_theme(state_key: str, theme_name: str) -> None:
    """Callback (on_click) d'un bouton de thème dans la barre latérale."""
    st.session_state[state_key] = theme_name


def theme_menu(
    themes: list,
    theme_levels: dict,
    state_key: str,
    counts: dict | None = None,
) -> str | None:
    """Affiche les thèmes dans la barre latérale, regroupés par niveau
    (séparateur + titre de niveau), et renvoie le thème sélectionné.

    Un st.radio ne permet pas d'insérer des séparateurs entre ses options :
    chaque thème est donc un bouton, et le thème choisi est gardé dans
    session_state[state_key] (clé non liée à un widget). counts (facultatif)
    ajoute un compteur au label : contrairement au format_func d'un radio,
    un label de bouton n'a pas de valeur persistée à perdre."""
    grouped_themes = [
        (level, [t for t in level_themes if t in themes])
        for level, level_themes in theme_levels.items()
    ]
    known_themes = {t for _, level_themes in grouped_themes for t in level_themes}
    other_themes = [t for t in themes if t not in known_themes]
    if other_themes:
        grouped_themes.append(("Autres", other_themes))

    for level, level_themes in grouped_themes:
        if not level_themes:
            continue
        st.divider()
        st.caption(level)
        for t in level_themes:
            label = t.replace("_", " ").title()
            count = (counts or {}).get(t, 0)
            st.button(
                f"{label} ({count})" if count else label,
                key=f"{state_key}_button_{t}",
                type="primary" if st.session_state.get(state_key) == t else "tertiary",
                width="stretch",
                on_click=select_theme,
                args=(state_key, t),
            )

    selected = st.session_state.get(state_key)
    return selected if selected in themes else None


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
            EXERCISE_STATE_CTE
            + "SELECT theme, "
            "COUNT(*) FILTER (WHERE last_reviewed <= CURRENT_DATE) AS due "
            "FROM exercise_state GROUP BY theme ORDER BY theme"
        ).df()
        due_by_theme = dict(zip(theme_counts_df["theme"], theme_counts_df["due"].astype(int)))
        st.metric("À réviser aujourd'hui", sum(due_by_theme.values()))

        st.markdown("**Que voulez-vous revoir ?**")
        theme = theme_menu(
            theme_counts_df["theme"].tolist(),
            EXERCISE_THEME_LEVELS,
            "selected_theme",
            counts=due_by_theme,
        )

        if theme:
            exercise = (
                con.execute(
                    EXERCISE_STATE_CTE
                    + "SELECT * FROM exercise_state WHERE theme = ? "
                    "ORDER BY last_reviewed, position",
                    [theme],
                )
                .df()
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

        st.markdown("**Thème à réviser ?**")
        flashcard_theme = theme_menu(
            flashcard_themes, FLASHCARD_THEME_LEVELS, "selected_flashcard_theme"
        )

    if not flashcard_themes:
        st.info("Aucune mémocard disponible pour l'instant.")
    elif not flashcard_theme:
        st.info("Sélectionnez un thème dans la barre à gauche")
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
