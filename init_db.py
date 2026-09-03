import io
import random
import pandas as pd
import duckdb

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

# ----------------------------------------
# EXERCISES LIST
# ----------------------------------------
data = {
    "theme": [
        "cross_joins", "cross_joins",
        "inner_joins", "inner_joins", "inner_joins",
        "left_joins", "left_joins", "left_joins", "left_joins",
        "outer_join",
        "self_joins",
    ],
    "exercise_name": [
        "beverages_and_food",
        "sizes_and_trademarks",
        "orders_and_order_details",
        "orders_details_and_customers",
        "orders_customers_and_products",
        "customers_orders_and_details",
        "customer_order_details_and_products",
        "store_customers_and_stores",
        "customer_stores_and_store_products",
        "stores_and_products_catalog",
        "meetings_with_benjamin",
    ],
    "statement": [
        "Associe chaque boisson à chaque plat pour générer toutes les combinaisons "
        "possibles (produit cartésien).",
        "Associe chaque taille à chaque marque pour générer toutes les combinaisons "
        "possibles (produit cartésien).",
        "Pour chaque commande, retrouve le produit commandé et la quantité en associant "
        "les commandes (orders) à leurs détails (order_details) via order_id.",
        "Ajoute le nom du client à chaque commande détaillée, en associant "
        "detailed_order à customers via "
        "customer_id.",
        "Ajoute le nom et le prix du produit à chaque commande, en associant "
        "order_client à products via "
        "product_id.",
        "Associe chaque client à ses commandes détaillées, même s'il n'a jamais "
        "commandé, en associant les clients (customers) aux commandes (orders) "
        "puis aux détails de commande (order_details) via des LEFT JOIN successifs.",
        "Ajoute le nom et le prix du produit à chaque commande client détaillée, même "
        "si le produit commandé n'existe pas dans le catalogue, en associant "
        "customer_order_details à products via "
        "un LEFT JOIN sur product_id.",
        "Associe chaque client à son magasin, même s'il n'en possède pas, en "
        "associant les clients (store_customers) aux magasins (stores) via un "
        "LEFT JOIN sur customer_id.",
        "Ajoute, pour chaque client et son magasin, les produits vendus dans ce "
        "magasin, en réalisant un LEFT JOIN avec store_products sur store_id.",
        "Complète les ventes de chaque magasin avec les informations du catalogue "
        "produit, même si un produit vendu ne figure plus au catalogue ou si un "
        "produit du catalogue n'est vendu dans aucun magasin, en réalisant un "
        "FULL OUTER JOIN avec product_catalog sur product_id.",
        "Retrouve les collègues qui étaient en réunion avec Benjamin, en "
        "réalisant une auto-jointure (self join) de merged_df sur elle-même "
        "via meeting_id, en gardant à gauche les lignes de Benjamin et en "
        "excluant Benjamin à droite.",
    ],
    "tables": [
        ["beverages", "food_items"],
        ["sizes", "trademarks"],
        ["orders", "order_details"],
        ["customers", "detailed_order"],
        ["order_client", "products"],
        ["customers", "orders", "order_details"],
        ["customer_order_details", "products"],
        ["store_customers", "stores"],
        ["customer_stores", "store_products"],
        ["stores_and_products", "product_catalog"],
        ["merged_df"],
    ],
    "last_reviewed": [
        "1980-01-01", "1970-01-01", "1970-01-01", "1970-01-01", "1970-01-01",
        "1970-01-01", "1970-01-01", "1970-01-01", "1970-01-01", "1970-01-01",
        "1970-01-01",
    ],
    # Position dans l'échelle de révision REVIEW_INTERVALS (app.py) : avance
    # d'un cran à chaque succès, retombe à 0 au premier échec.
    "interval_step": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}
memory_state_df = pd.DataFrame(data)
con.execute("CREATE TABLE IF NOT EXISTS memory_state AS SELECT * FROM memory_state_df")

# Si la base existe déjà (memory_state pré-existant), on ajoute seulement les
# exercices absents plutôt que de recréer la table : ça évite d'écraser la
# progression (last_reviewed / interval_step) des exercices déjà en cours.
con.execute("""
    INSERT INTO memory_state
    SELECT n.* FROM memory_state_df n
    WHERE NOT EXISTS (
        SELECT 1 FROM memory_state m WHERE m.exercise_name = n.exercise_name
    )
""")

# ----------------------------------------
# CROSS JOIN EXERCISES
# ----------------------------------------

CSV = """
beverage,price
orange juice,2.5
Expresso,2
Tea,3
"""
beverages = pd.read_csv(io.StringIO(CSV))
con.execute("CREATE TABLE IF NOT EXISTS beverages AS SELECT * FROM beverages")

CSV2 = """
food_item,food_price
cookie juice,2.5
chocolatine,2
muffin,3
"""
food_items = pd.read_csv(io.StringIO(CSV2))
con.execute("CREATE TABLE IF NOT EXISTS food_items AS SELECT * FROM food_items")

sizes = '''
size
XS
M
L
XL
'''
sizes = pd.read_csv(io.StringIO(sizes))
con.execute("CREATE TABLE IF NOT EXISTS sizes AS SELECT * FROM sizes")

trademarks = '''
trademark
Nike
Asphalte
Abercrombie
Lewis
'''
trademarks = pd.read_csv(io.StringIO(trademarks))
con.execute("CREATE TABLE IF NOT EXISTS trademarks AS SELECT * FROM trademarks")


# ----------------------------------------
# INNER JOIN EXERCISES
# ----------------------------------------

orders_data = {
    "order_id": [1, 2, 3, 4, 5],
    "customer_id": [101, 102, 103, 104, 105],
}
orders = pd.DataFrame(orders_data)
con.execute("CREATE TABLE IF NOT EXISTS orders AS SELECT * FROM orders")

customers_data = {
    "customer_id": [101, 102, 103, 104, 105, 106],
    "customer_name": ["Toufik", "Daniel", "Tancrède", "Kaouter", "Jean-Nicolas", "David"],
}
customers = pd.DataFrame(customers_data)
con.execute("CREATE TABLE IF NOT EXISTS customers AS SELECT * FROM customers")

p_names = ["Laptop", "Ipad", "Livre", "Petitos"]
products_data = {
    "product_id": [101, 103, 104, 105],
    "product_name": p_names,
    "product_price": [800, 400, 30, 2],
}
products = pd.DataFrame(products_data)
con.execute("CREATE TABLE IF NOT EXISTS products AS SELECT * FROM products")

order_details_data = {
    "order_id": [1, 2, 3, 4, 5],
    "product_id": [102, 104, 101, 103, 105],
    "quantity": [2, 1, 3, 2, 1],
}
order_details = pd.DataFrame(order_details_data)
con.execute("CREATE TABLE IF NOT EXISTS order_details AS SELECT * FROM order_details")

# Table "detailed_order" : résultat attendu de l'exercice 1 (orders INNER JOIN
# order_details), matérialisée pour servir de point de départ à l'exercice 2
# sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS detailed_order AS
    SELECT * FROM orders
    INNER JOIN order_details
    USING (order_id)
""")

# Table "order_client" : résultat attendu de l'exercice 2 (customers INNER JOIN
# detailed_order), matérialisée pour servir de point de départ à l'exercice 3
# sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS order_client AS
    SELECT customers.customer_id,
        customer_name,
        order_id,
        product_id,
        quantity
    FROM customers
    INNER JOIN detailed_order
    ON customers.customer_id = detailed_order.customer_id
""")


# ----------------------------------------
# LEFT JOIN EXERCISES
# ----------------------------------------

# Table "customer_order_details" : résultat attendu de l'exercice 1 (customers
# LEFT JOIN orders LEFT JOIN order_details), matérialisée pour servir de
# point de départ à l'exercice 2 sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS customer_order_details AS
    SELECT * FROM customers
    LEFT JOIN orders
    USING (customer_id)
    LEFT JOIN order_details
    USING (order_id)
""")


# ----------------------------------------
# LEFT JOIN EXERCISES (SET 2) + OUTER JOIN EXERCISE
# ----------------------------------------
# Nouveau jeu de tables (store_customers / stores / store_products /
# product_catalog) : noms distincts de customers/products ci-dessus pour ne
# pas entrer en collision avec les tables du pipeline inner_joins/left_joins.

store_customers_data = {
    "customer_id": [11, 12, 13, 14, 15],
    "customer_name": ["Zeinaba", "Tancrède", "Israel", "Kaouter", "Alan"],
}
store_customers = pd.DataFrame(store_customers_data)
con.execute("CREATE TABLE IF NOT EXISTS store_customers AS SELECT * FROM store_customers")

stores_data = {
    "store_id": [1, 2, 3, 4],
    "customer_id": [11, 12, 13, 15],
}
stores = pd.DataFrame(stores_data)
con.execute("CREATE TABLE IF NOT EXISTS stores AS SELECT * FROM stores")

store_products_data = {
    "store_id": [1, 1, 1, 2, 2, 3, 4],
    "product_id": [101, 103, 105, 101, 103, 104, 105],
}
store_products = pd.DataFrame(store_products_data)
con.execute("CREATE TABLE IF NOT EXISTS store_products AS SELECT * FROM store_products")

product_catalog_names = ["Cherry coke", "Laptop", "Ipad", "Livre"]
product_catalog_data = {
    "product_id": [100, 101, 103, 104],
    "product_name": product_catalog_names,
    "product_price": [3, 800, 400, 30],
}
product_catalog = pd.DataFrame(product_catalog_data)
con.execute("CREATE TABLE IF NOT EXISTS product_catalog AS SELECT * FROM product_catalog")

# Table "customer_stores" : résultat attendu de l'exercice 1 (store_customers
# LEFT JOIN stores), matérialisée pour servir de point de départ à
# l'exercice 2 sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS customer_stores AS
    SELECT * FROM store_customers
    LEFT JOIN stores
    USING (customer_id)
""")

# Table "stores_and_products" : résultat attendu de l'exercice 2
# (customer_stores LEFT JOIN store_products), matérialisée pour servir de
# point de départ à l'exercice outer_join sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS stores_and_products AS
    SELECT * FROM customer_stores
    LEFT JOIN store_products
    USING (store_id)
""")

# ----------------------------------------
# SELF JOIN EXERCISE
# ----------------------------------------
# Nouveau jeu de données (réunions/participants), indépendant des tables
# précédentes : simule des réunions avec des participants aléatoires, pour
# l'exercice self join (retrouver les collègues de Benjamin en réunion).

random.seed(42)
person_names = ["Benjamin", "Florian", "Tarik", "Bob", "Sirine", "Alice"]

meetings_data = []
for meeting_id in range(150):
    persons_in_meet = random.sample(person_names, random.randint(1, 5))
    for person_name in persons_in_meet:
        meetings_data.append((meeting_id, person_name))
meetings_df = pd.DataFrame(meetings_data, columns=["meeting_id", "person_name"])

meeting_durations = []
for meeting_id in meetings_df["meeting_id"].unique():
    duration = random.randint(10, 60)
    meeting_durations.append((meeting_id, duration))
durations_df = pd.DataFrame(meeting_durations, columns=["meeting_id", "duration_minutes"])

merged_df = meetings_df.merge(durations_df, on="meeting_id")
con.execute("CREATE TABLE IF NOT EXISTS merged_df AS SELECT * FROM merged_df")

# ----------------------------------------
# FLASHCARDS (memocards) - fonctions SQL a retenir
# ----------------------------------------
# Contrairement aux exercices ci-dessus (requête à écrire, comparée à une
# solution), une flashcard est une simple paire question/réponse pour la
# mémorisation de syntaxe. Table séparée de memory_state : pas de notion de
# "tables" utilisées, mais même logique de planification (last_reviewed /
# interval_step) pour pouvoir réutiliser REVIEW_INTERVALS plus tard.
# Pour le moment : uniquement le thème "stats", en syntaxe SQL pure (pas
# d'équivalent pandas, pour ne pas mélanger les deux dans une même carte).

flashcards_data = {
    "theme": (
        ["stats"] * 6
        + ["window_functions"] * 6
        + ["cte"] * 1
        + ["joins"] * 5
        + ["null_filtering"] * 3
        + ["aggregates"] * 2
        + ["sets"] * 1
        + ["dates"] * 5
        + ["strings"] * 6
    ),
    "card_name": [
        # stats
        "moyenne_avg",
        "ecart_type_echantillon",
        "ecart_type_population",
        "group_by",
        "coalesce",
        "cast",
        # window_functions
        "row_number",
        "rank",
        "dense_rank",
        "lag",
        "lead",
        "partition_by",
        # cte
        "cte_syntax",
        # joins
        "inner_join",
        "left_join",
        "full_outer_join",
        "cross_join",
        "self_join",
        # null_filtering
        "where_vs_having",
        "nullif",
        "is_null",
        # aggregates
        "count_star_vs_column",
        "distinct",
        # sets
        "union_vs_union_all",
        # dates
        "current_date",
        "extract_date_part",
        "date_diff",
        "date_add_interval",
        "date_trunc",
        # strings
        "concat_strings",
        "substring",
        "upper_lower",
        "trim",
        "length_string",
        "like_pattern",
    ],
    "question": [
        # stats
        "Comment calculer la moyenne d'une colonne en SQL ?",
        "Comment calculer l'écart-type d'échantillon (le plus courant, "
        "équivalent au .std() par défaut de pandas) en SQL ?",
        "Comment calculer l'écart-type de population en SQL ?",
        "Comment regrouper les lignes par une colonne avant d'agréger "
        "(SUM, COUNT, AVG...) ?",
        "Comment remplacer les valeurs NULL d'une colonne par une valeur "
        "par défaut ?",
        "Comment convertir une colonne vers le type integer ?",
        # window_functions
        "Comment numéroter chaque ligne de façon unique, même en cas "
        "d'égalité (window function) ?",
        "Comment classer les lignes avec des trous en cas d'ex-aequo "
        "(ex : 1, 1, 3) ?",
        "Comment classer les lignes sans trou en cas d'ex-aequo "
        "(ex : 1, 1, 2) ?",
        "Comment récupérer la valeur de la ligne précédente dans une "
        "window function ?",
        "Comment récupérer la valeur de la ligne suivante dans une "
        "window function ?",
        "Quelle clause découpe les lignes en groupes pour une window "
        "function, sans réduire le nombre de lignes (contrairement à "
        "GROUP BY) ?",
        # cte
        "Comment écrire une CTE (Common Table Expression) ?",
        # joins
        "Quel JOIN ne garde que les lignes présentes dans les deux "
        "tables ?",
        "Quel JOIN garde toutes les lignes de la table de gauche, avec "
        "NULL côté droit si pas de correspondance ?",
        "Quel JOIN garde toutes les lignes des deux tables, avec NULL du "
        "côté manquant ?",
        "Quel JOIN génère toutes les combinaisons possibles entre deux "
        "tables (produit cartésien) ?",
        "Comment appelle-t-on une jointure d'une table sur elle-même ?",
        # null_filtering
        "Quelle est la différence entre WHERE et HAVING ?",
        "Comment éviter une division par zéro en remplaçant une valeur "
        "par NULL si elle est égale à une autre ?",
        "Comment tester si une valeur est NULL ?",
        # aggregates
        "Quelle est la différence entre COUNT(*) et COUNT(colonne) ?",
        "Comment éliminer les doublons dans un résultat ?",
        # sets
        "Quelle est la différence entre UNION et UNION ALL ?",
        # dates
        "Comment récupérer la date du jour ?",
        "Comment extraire une partie d'une date (année, mois, jour...) ?",
        "Comment calculer le nombre de jours entre deux dates ?",
        "Comment ajouter un intervalle de temps à une date (ex : +7 "
        "jours) ?",
        "Comment tronquer une date au début du mois (ou de la semaine, "
        "année...) ?",
        # strings
        "Comment concaténer deux chaînes de caractères ?",
        "Comment extraire une sous-chaîne à partir d'une position "
        "donnée ?",
        "Comment convertir une chaîne en majuscules / minuscules ?",
        "Comment supprimer les espaces en début et fin de chaîne ?",
        "Comment obtenir la longueur d'une chaîne de caractères ?",
        "Comment rechercher un motif (wildcard) dans une chaîne ?",
    ],
    "answer": [
        # stats
        "AVG(colonne)",
        "STDDEV(colonne)  -- alias de STDDEV_SAMP(colonne)",
        "STDDEV_POP(colonne)",
        "GROUP BY colonne",
        "COALESCE(colonne, valeur_par_defaut)",
        "CAST(colonne AS INTEGER)",
        # window_functions
        "ROW_NUMBER() OVER (ORDER BY colonne)",
        "RANK() OVER (ORDER BY colonne)",
        "DENSE_RANK() OVER (ORDER BY colonne)",
        "LAG(colonne) OVER (ORDER BY ...)",
        "LEAD(colonne) OVER (ORDER BY ...)",
        "PARTITION BY colonne",
        # cte
        "WITH nom AS (SELECT ...) SELECT ... FROM nom",
        # joins
        "INNER JOIN",
        "LEFT JOIN",
        "FULL OUTER JOIN",
        "CROSS JOIN",
        "self join  -- la même table jointe à elle-même via deux alias",
        # null_filtering
        "WHERE filtre avant le GROUP BY (lignes brutes), HAVING filtre "
        "après (sur le résultat agrégé)",
        "NULLIF(colonne, 0)",
        "IS NULL / IS NOT NULL  -- jamais '= NULL', NULL n'est égal à rien",
        # aggregates
        "COUNT(*) compte toutes les lignes, COUNT(colonne) ignore les "
        "NULL de cette colonne",
        "SELECT DISTINCT colonne",
        # sets
        "UNION déduplique les résultats (donc plus lent), UNION ALL "
        "garde tous les doublons",
        # dates
        "CURRENT_DATE  -- ou CURRENT_TIMESTAMP pour la date+heure",
        "EXTRACT(YEAR FROM colonne)  -- standard ANSI, portable",
        "date_fin - date_debut  -- Postgres/DuckDB (résultat en jours) ; "
        "DATEDIFF(date_fin, date_debut) en MySQL, "
        "DATEDIFF(day, date_debut, date_fin) en SQL Server (l'ordre des "
        "arguments change selon le SGBD, piège classique)",
        "date_colonne + INTERVAL '7 days'  -- Postgres/DuckDB ; "
        "DATE_ADD(date_colonne, INTERVAL 7 DAY) en MySQL",
        "DATE_TRUNC('month', colonne)  -- Postgres/DuckDB, pas MySQL",
        # strings
        "colonne1 || colonne2  -- standard ANSI ; CONCAT(colonne1, "
        "colonne2) marche presque partout aussi",
        "SUBSTRING(colonne, position, longueur)",
        "UPPER(colonne) / LOWER(colonne)",
        "TRIM(colonne)",
        "LENGTH(colonne)  -- LEN(colonne) en SQL Server",
        "colonne LIKE '%motif%'  -- % = plusieurs caractères, _ = un "
        "seul ; ILIKE (Postgres/DuckDB) pour ignorer la casse",
    ],
    "last_reviewed": ["1970-01-01"] * 35,
    "interval_step": [0] * 35,
}
flashcards_df = pd.DataFrame(flashcards_data)
con.execute("CREATE TABLE IF NOT EXISTS flashcards AS SELECT * FROM flashcards_df")

# Même logique que pour memory_state : on n'ajoute que les cartes absentes,
# pour ne pas écraser la progression de révision des cartes déjà en place.
con.execute("""
    INSERT INTO flashcards
    SELECT n.* FROM flashcards_df n
    WHERE NOT EXISTS (
        SELECT 1 FROM flashcards m WHERE m.card_name = n.card_name
    )
""")

con.close()
