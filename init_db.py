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
        "aggregation", "aggregation", "aggregation",
        "aggregation", "aggregation", "aggregation",
        # Niveau 2 : self join (suite), CTE, CRUD
        "self_joins", "self_joins",
        "cte", "cte", "cte", "cte",
        "crud", "crud", "crud", "crud",
        # Niveau 3 : HAVING / COUNT(DISTINCT), CASE WHEN, GROUPING SETS
        "aggregation", "aggregation", "aggregation",
        "case_when", "case_when", "case_when", "case_when",
        "grouping_sets", "grouping_sets", "grouping_sets",
        "grouping_sets", "grouping_sets",
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
        "total_sales_per_client",
        "average_basket_per_client",
        "sales_count_per_client",
        "sales_stats_per_client",
        "top_3_clients_by_revenue",
        "clients_above_average_basket",
        "employees_and_manager_n2",
        "employees_without_reports",
        "order_amounts_with_cte",
        "customers_without_valid_order",
        "benjamin_colleagues_meeting_time",
        "client_revenue_share",
        "insert_missing_product",
        "raise_expensive_products_price",
        "delete_customers_without_orders",
        "archive_big_sales",
        "departments_payroll_above_300k",
        "lines_and_distinct_products_per_store",
        "departments_headcount_above_wage_floor",
        "wage_bands",
        "headcount_per_wage_band",
        "revenue_per_product_with_discounts",
        "orders_by_discount_status",
        "product_totals_with_grand_total",
        "regional_average_population_subtotals",
        "department_population_2021_rollup",
        "store_product_cube",
        "quantity_per_discount_code_with_total",
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
        "Calcule le montant total des ventes (chiffre d'affaires) pour "
        "chaque client, en regroupant sales avec GROUP BY sur "
        "client_name.",
        "Calcule le panier moyen (montant moyen par vente) de chaque "
        "client, en regroupant sales avec GROUP BY sur client_name.",
        "Compte le nombre de ventes réalisées par chaque client, en "
        "regroupant sales avec GROUP BY sur client_name.",
        "Retrouve, pour chaque client, sa plus petite vente, sa plus "
        "grande vente et l'écart-type de ses ventes (variabilité du "
        "panier), en regroupant sales avec GROUP BY sur client_name.",
        "Retrouve les 3 clients ayant généré le plus de chiffre "
        "d'affaires, du plus grand au plus petit.",
        "Retrouve les clients dont le panier moyen dépasse la moyenne "
        "générale des paniers moyens (moyenne des moyennes par client), "
        "en utilisant deux CTE plutôt qu'une sous-requête : une pour le "
        "panier moyen par client, une pour la moyenne générale.",
        # self_joins
        "Pour chaque employé qui a un N+2 (le manager de son manager), "
        "affiche son nom et celui de son N+2. Les employés sans N+2 ne "
        "doivent pas apparaître.",
        "Retrouve les employés qui ne managent personne (aucun employé "
        "n'a leur employee_id comme manager_id), avec une auto-jointure "
        "plutôt qu'une sous-requête.",
        # cte
        "Calcule le montant de chaque commande (quantity × product_price) "
        "avec le nom du client, en une seule requête : une CTE pour "
        "valoriser les lignes de commande, sans passer par les tables "
        "intermédiaires detailed_order / order_client. Les commandes dont "
        "le produit n'existe pas dans products sont exclues.",
        "Retrouve les clients qui n'ont aucune commande valide, c'est-à-dire "
        "aucune commande portant sur un produit présent dans products "
        "(clients sans commande inclus). Construis d'abord les commandes "
        "valides dans une CTE.",
        "Pour chaque collègue de Benjamin, compte le nombre de réunions "
        "partagées avec lui et la durée totale (en minutes) de ces "
        "réunions. Isole d'abord les réunions de Benjamin dans une CTE.",
        "Calcule, pour chaque client, son chiffre d'affaires total et sa "
        "part dans le chiffre d'affaires global, en pourcentage arrondi à "
        "2 décimales (ROUND). Utilise deux CTE (CA par client, CA global) "
        "plutôt qu'une sous-requête.",
        # crud
        "Le produit 102 apparaît dans order_details mais pas dans le "
        "catalogue : ajoute-le à products, avec le nom 'Casque' et le prix "
        "150. (Le résultat comparé est la table products après ta requête.)",
        "Augmente de 50 le prix de tous les produits de products qui "
        "coûtent plus de 100. (Le résultat comparé est la table products "
        "après ta requête.)",
        "Supprime de customers les clients qui n'ont passé aucune commande "
        "(absents de orders). Isole-les d'abord dans une CTE. (Le résultat "
        "comparé est la table customers après ta requête.)",
        "Archive dans sales_archive (vide pour l'instant) toutes les ventes "
        "de sales d'un montant supérieur ou égal à 60, en une seule "
        "requête INSERT ... SELECT. (Le résultat comparé est la table "
        "sales_archive après ta requête.)",
        # aggregation (niveau 3) : HAVING, COUNT(DISTINCT)
        "Retrouve les départements de wages dont la masse salariale "
        "(somme des salaires) dépasse 300 000. Affiche le département et "
        "sa masse salariale. Une seule requête, sans CTE.",
        "Pour chaque magasin de store_sales, affiche le nombre de lignes "
        "de vente et le nombre de produits différents vendus. Attention : "
        "un même produit peut apparaître sur plusieurs lignes d'un "
        "magasin.",
        "En ne comptant que les salariés payés au moins 65 000, retrouve "
        "les départements qui en ont au moins 4. Affiche le département, "
        "ce nombre de salariés et leur salaire moyen.",
        # case_when
        "Classe chaque salarié de wages dans une tranche : 'Junior' en "
        "dessous de 70 000, 'Confirmed' de 70 000 à moins de 90 000, "
        "'Senior' à partir de 90 000. Affiche name, wage et la tranche.",
        "Avec les mêmes tranches ('Junior' < 70 000, 'Confirmed' < 90 000, "
        "'Senior' au-delà), affiche pour chaque tranche le nombre de "
        "salariés et la masse salariale. Calcule la tranche dans une CTE.",
        "Calcule le chiffre d'affaires net par product_id dans "
        "orders_discounts : quantity × price_per_unit, avec -10 % pour le "
        "code 'DISCOUNT10', -20 % pour 'DISCOUNT20', et aucune remise pour "
        "les autres codes ou sans code. Calcule le CA de chaque commande "
        "dans une CTE.",
        "Classe chaque commande de orders_discounts selon son code : "
        "'no_code' si elle n'a pas de code, 'valid_code' pour 'DISCOUNT10' "
        "ou 'DISCOUNT20', 'invalid_code' sinon. Pour chaque statut, affiche "
        "le nombre de commandes et le CA brut (quantity × price_per_unit, "
        "sans remise).",
        # grouping_sets
        "Affiche le montant total vendu par produit dans store_sales "
        "(tous magasins confondus), plus une ligne de total général "
        "(product_name à NULL). Une seule requête GROUP BY, sans UNION.",
        "Dans regional_population, affiche la population de chaque région "
        "pour chaque année, plus, pour chaque région, une ligne de "
        "sous-total (year à NULL) qui donne sa population MOYENNE sur la "
        "période. Colonnes : region, year, population moyenne. Une seule "
        "requête GROUP BY.",
        "Pour l'année 2021 uniquement, affiche à partir de "
        "department_population la population de chaque département, le "
        "sous-total de chaque région (department à NULL) et le total "
        "national (region et department à NULL). Colonnes : region, "
        "department, population. Les dimensions sont hiérarchiques : "
        "choisis l'opérateur adapté.",
        "Dans store_sales, magasin et produit sont deux axes indépendants. "
        "Affiche le montant total pour chaque combinaison magasin × "
        "produit, pour chaque magasin, pour chaque produit, et le total "
        "général. Colonnes : store_id, product_name, montant total.",
        "Affiche la quantité totale commandée par discount_code dans "
        "orders_discounts, plus une ligne de total. Problème : les "
        "commandes sans code et la ligne de total auraient toutes les deux "
        "un discount_code NULL. Distingue-les avec la fonction GROUPING() : "
        "libellé 'NO_CODE' pour les commandes sans code, 'TOTAL' pour la "
        "ligne de total, le code lui-même sinon. Colonnes : libellé, "
        "quantité totale.",
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
        ["sales"],
        ["sales"],
        ["sales"],
        ["sales"],
        ["sales"],
        ["sales"],
        ["employees"],
        ["employees"],
        ["orders", "order_details", "customers", "products"],
        ["customers", "orders", "order_details", "products"],
        ["merged_df"],
        ["sales"],
        # crud : la PREMIÈRE table de la liste est celle dont l'état final
        # est comparé à la solution (voir run_dml_in_sandbox dans app.py).
        ["products", "order_details"],
        ["products"],
        ["customers", "orders"],
        ["sales_archive", "sales"],
        # aggregation (niveau 3)
        ["wages"],
        ["store_sales"],
        ["wages"],
        # case_when
        ["wages"],
        ["wages"],
        ["orders_discounts"],
        ["orders_discounts"],
        # grouping_sets
        ["store_sales"],
        ["regional_population"],
        ["department_population"],
        ["store_sales"],
        ["orders_discounts"],
    ],
}
nb_exercises = len(data["exercise_name"])
data["last_reviewed"] = ["1980-01-01"] + ["1970-01-01"] * (nb_exercises - 1)
# Position dans l'échelle de révision REVIEW_INTERVALS (app.py) : avance
# d'un cran à chaque succès, retombe à 0 au premier échec.
data["interval_step"] = [0] * nb_exercises
memory_state_df = pd.DataFrame(data)
con.execute("CREATE TABLE IF NOT EXISTS memory_state AS SELECT * FROM memory_state_df")

# Si la base existe déjà (memory_state pré-existant), on ajoute seulement les
# exercices absents plutôt que de recréer la table : ça évite d'écraser la
# progression (last_reviewed / interval_step) des exercices déjà en cours.
con.execute("""
    INSERT INTO memory_state
        (theme, exercise_name, statement, tables, last_reviewed, interval_step)
    SELECT n.theme, n.exercise_name, n.statement, n.tables,
        n.last_reviewed, n.interval_step
    FROM memory_state_df n
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
# AGGREGATION EXERCISES
# ----------------------------------------
# Jeu de données fourni par l'utilisateur : 10 clients, et une liste de 15
# montants de vente dupliquée (*2, donc 30 ventes). Le mapping vente -> client
# n'était pas précisé : on mélange les montants (seed fixe, pour rester
# reproductible) puis on les distribue à tour de rôle sur les 10 clients, ce
# qui donne exactement 3 ventes par client. Sans ce mélange, distribuer une
# liste doublée directement (round-robin ou par blocs) recrée mécaniquement
# les 2 mêmes paniers pour des clients différents (30 = 2 x 15 = 3 x 10).

random.seed(42)
clients = [
    "Oussama", "Julie", "Chris", "Tom", "Jean-Nicolas",
    "Aline", "Ben", "Toufik", "Sylvie", "David",
]
ventes = [110, 49, 65, 23, 24, 3.99, 29, 48.77, 44, 10, 60, 12, 62, 19, 75] * 2
random.shuffle(ventes)

sales_data = {
    "client_name": [clients[i % len(clients)] for i in range(len(ventes))],
    "amount": ventes,
}
sales = pd.DataFrame(sales_data)
con.execute("CREATE TABLE IF NOT EXISTS sales AS SELECT * FROM sales")

# ----------------------------------------
# LEVEL 2 : SELF JOIN (SUITE), CTE, CRUD
# ----------------------------------------
# employees : dataset du cours Data Upskilling (self join n+2), repris tel
# quel. Hiérarchie : Sylvie (12) > Daniel (13) > Sophie (11), Kaouter (14) ;
# Sophie (11) > David (15).
con.execute("""
    CREATE TABLE IF NOT EXISTS employees AS
    SELECT * FROM (VALUES
        (11, 'Sophie', 13),
        (12, 'Sylvie', NULL),
        (13, 'Daniel', 12),
        (14, 'Kaouter', 13),
        (15, 'David', 11)
    ) AS t(employee_id, employee_name, manager_id)
""")

# sales_archive : table cible (vide) de l'exercice CRUD INSERT ... SELECT.
# Les exercices CRUD sont exécutés dans une transaction annulée ensuite
# (ROLLBACK, voir app.py) : cette table reste donc vide en base.
con.execute("""
    CREATE TABLE IF NOT EXISTS sales_archive (
        client_name VARCHAR,
        amount DOUBLE
    )
""")

# ----------------------------------------
# LEVEL 3 : HAVING, COUNT(DISTINCT), CASE WHEN, GROUPING SETS / ROLLUP / CUBE
# ----------------------------------------
# Datasets du cours Data Upskilling (noms traduits en anglais). Les
# exercices en sont des variantes, pas les questions du cours.

# store_sales (cours : df "redbull"). Armentieres a DEUX lignes redbull à 45 :
# piège COUNT(*) vs COUNT(DISTINCT product_name).
con.execute("""
    CREATE TABLE IF NOT EXISTS store_sales AS
    SELECT * FROM (VALUES
        ('Armentieres', 'redbull', 45), ('Armentieres', 'chips', 60),
        ('Armentieres', 'wine', 60), ('Armentieres', 'redbull', 45),
        ('Lille', 'redbull', 100), ('Lille', 'chips', 140),
        ('Lille', 'wine', 190), ('Lille', 'icecream', 170),
        ('Douai', 'redbull', 55), ('Douai', 'chips', 70),
        ('Douai', 'wine', 20), ('Douai', 'icecream', 45)
    ) AS t(store_id, product_name, amount)
""")

# wages (cours : wages). Aucune égalité de salaire.
con.execute("""
    CREATE TABLE IF NOT EXISTS wages AS
    SELECT * FROM (VALUES
        ('Toufik', 60000, 'IT'), ('Jean-Nicolas', 75000, 'HR'),
        ('Daniel', 55000, 'SALES'), ('Kaouter', 80000, 'IT'),
        ('Sylvie', 70000, 'IT'), ('Sebastien', 90000, 'HR'),
        ('Diane', 65000, 'SALES'), ('Romain', 72000, 'IT'),
        ('Francois', 68000, 'HR'), ('Anna', 85000, 'SALES'),
        ('Zeinaba', 100000, 'IT'), ('Gregory', 120000, 'IT'),
        ('Karima', 95000, 'HR'), ('Arthur', 83000, 'SALES'),
        ('Benjamin', 110000, 'CEO')
    ) AS t(name, wage, department)
""")

# orders_discounts (cours : codes de réduction). discount_code NULL = pas de
# code ; 'UNKNOWN' = code invalide (aucune remise).
con.execute("""
    CREATE TABLE IF NOT EXISTS orders_discounts (
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price_per_unit DOUBLE,
        discount_code VARCHAR
    )
""")
con.execute("""
    INSERT INTO orders_discounts
    SELECT * FROM (VALUES
        (1, 101, 5, 10.0, NULL), (2, 102, 3, 25.0, 'DISCOUNT10'),
        (3, 101, 2, 10.0, 'DISCOUNT20'), (4, 103, 4, 8.0, NULL),
        (5, 102, 6, 25.0, NULL), (6, 103, 2, 8.0, 'UNKNOWN')
    ) AS t(order_id, product_id, quantity, price_per_unit, discount_code)
    WHERE NOT EXISTS (SELECT 1 FROM orders_discounts)
""")

# regional_population (cours : dfpop).
con.execute("""
    CREATE TABLE IF NOT EXISTS regional_population AS
    SELECT * FROM (VALUES
        (2016, 'IDF', 1010000), (2017, 'IDF', 1020000), (2018, 'IDF', 1030000),
        (2019, 'IDF', 1040000), (2020, 'IDF', 1000000),
        (2016, 'HDF', 910000), (2017, 'HDF', 920000), (2018, 'HDF', 930000),
        (2019, 'HDF', 940000), (2020, 'HDF', 900000),
        (2016, 'PACA', 810000), (2017, 'PACA', 820000), (2018, 'PACA', 830000),
        (2019, 'PACA', 840000), (2020, 'PACA', 950000)
    ) AS t(year, region, population)
""")

# department_population (cours : dpts_dfs). 2016 = valeurs du cours ;
# 2017-2021 = synthétique (+0,3 %/an, arrondi), pour avoir plusieurs années.
department_population_2016 = [
    ("HDF", "59", 2603723), ("HDF", "62", 1470725),
    ("IDF", "75", 2190327), ("IDF", "95", 1221923),
    ("PACA", "83", 1055821), ("PACA", "84", 559014),
]
department_population = pd.DataFrame(
    [
        (year, region, department, round(population_2016 * (1 + 0.003 * (year - 2016))))
        for year in range(2016, 2022)
        for region, department, population_2016 in department_population_2016
    ],
    columns=["year", "region", "department", "population"],
)
con.execute(
    "CREATE TABLE IF NOT EXISTS department_population AS "
    "SELECT * FROM department_population"
)

# ----------------------------------------
# FLASHCARDS (memocards) - fonctions SQL a retenir
# ----------------------------------------
# Contrairement aux exercices ci-dessus (requête à écrire, comparée à une
# solution), une flashcard est une simple paire question/réponse pour la
# mémorisation de syntaxe, accompagnée d'un exemple de requête concret
# (colonne "example", affiché sous la réponse dans l'app) pour visualiser
# la syntaxe en contexte. Table séparée de memory_state : pas de notion de
# "tables" utilisées, mais même logique de planification (last_reviewed /
# interval_step) pour pouvoir réutiliser REVIEW_INTERVALS plus tard.
# En syntaxe SQL pure (pas d'équivalent pandas, pour ne pas mélanger les
# deux dans une même carte).

flashcards_data = {
    "theme": (
        ["stats"] * 6
        + ["window_functions"] * 6
        + ["cte"] * 2
        + ["joins"] * 6
        + ["null_filtering"] * 4
        + ["aggregates"] * 3
        + ["sets"] * 1
        + ["dates"] * 5
        + ["strings"] * 6
        + ["crud"] * 4
        + ["case_when"] * 2
        + ["grouping_sets"] * 4
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
        "multiple_ctes",
        # joins
        "inner_join",
        "left_join",
        "full_outer_join",
        "cross_join",
        "self_join",
        "anti_join",
        # null_filtering
        "where_vs_having",
        "nullif",
        "is_null",
        "logical_query_order",
        # aggregates
        "count_star_vs_column",
        "distinct",
        "count_distinct",
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
        # crud
        "insert_values",
        "insert_select",
        "update_set",
        "delete_where",
        # case_when
        "case_when_syntax",
        "case_when_null",
        # grouping_sets
        "grouping_sets",
        "rollup",
        "cube",
        "grouping_function",
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
        "Comment enchaîner plusieurs CTE dans une même requête ?",
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
        "Comment retrouver les lignes de A qui n'ont AUCUNE correspondance "
        "dans B, sans sous-requête (anti-join) ?",
        # null_filtering
        "Quelle est la différence entre WHERE et HAVING ?",
        "Comment éviter une division par zéro en remplaçant une valeur "
        "par NULL si elle est égale à une autre ?",
        "Comment tester si une valeur est NULL ?",
        "Dans quel ordre logique une requête SELECT est-elle évaluée ?",
        # aggregates
        "Quelle est la différence entre COUNT(*) et COUNT(colonne) ?",
        "Comment éliminer les doublons dans un résultat ?",
        "Comment compter le nombre de valeurs différentes d'une colonne "
        "(par groupe) ?",
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
        # crud
        "Comment ajouter une ligne à une table ?",
        "Comment insérer dans une table le résultat d'une requête ?",
        "Comment modifier des lignes existantes ?",
        "Comment supprimer des lignes ?",
        # case_when
        "Comment créer une colonne dont la valeur dépend de conditions "
        "(équivalent d'un if / elif / else) ?",
        "Pourquoi CASE WHEN colonne = NULL ne marche jamais, et que renvoie "
        "un CASE sans ELSE quand aucune condition n'est vraie ?",
        # grouping_sets
        "Comment calculer en une seule requête plusieurs niveaux "
        "d'agrégation choisis (ex : détail magasin × produit + sous-total "
        "par magasin) ?",
        "Quel opérateur calcule les sous-totaux d'une hiérarchie (année > "
        "région > département) plus le total général ?",
        "Quel opérateur calcule les agrégats pour TOUTES les combinaisons "
        "de colonnes (axes indépendants) ?",
        "Comment distinguer, dans un ROLLUP / GROUPING SETS, un NULL de "
        "sous-total d'un vrai NULL présent dans les données ?",
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
        "WITH a AS (...), b AS (SELECT ... FROM a) SELECT ...  -- un seul "
        "WITH, CTE séparées par des virgules, chacune peut lire les "
        "précédentes",
        # joins
        "INNER JOIN",
        "LEFT JOIN",
        "FULL OUTER JOIN",
        "CROSS JOIN",
        "self join  -- la même table jointe à elle-même via deux alias",
        "A LEFT JOIN B ON ... WHERE B.cle IS NULL",
        # null_filtering
        "WHERE filtre avant le GROUP BY (lignes brutes), HAVING filtre "
        "après (sur le résultat agrégé)",
        "NULLIF(colonne, 0)",
        "IS NULL / IS NOT NULL  -- jamais '= NULL', NULL n'est égal à rien",
        "FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY  -- "
        "d'où l'impossibilité d'utiliser un alias du SELECT ou un agrégat "
        "dans le WHERE",
        # aggregates
        "COUNT(*) compte toutes les lignes, COUNT(colonne) ignore les "
        "NULL de cette colonne",
        "SELECT DISTINCT colonne",
        "COUNT(DISTINCT colonne)  -- ignore aussi les NULL",
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
        # crud
        "INSERT INTO table (col1, col2) VALUES (v1, v2)",
        "INSERT INTO table (col1, col2) SELECT ... FROM ...  -- pas de "
        "VALUES",
        "UPDATE table SET colonne = valeur WHERE ...  -- sans WHERE, "
        "TOUTES les lignes sont modifiées",
        "DELETE FROM table WHERE ...  -- sans WHERE, la table est vidée",
        # case_when
        "CASE WHEN condition1 THEN valeur1 WHEN condition2 THEN valeur2 "
        "ELSE valeur_par_defaut END  -- conditions testées dans l'ordre, la "
        "première vraie gagne",
        "NULL n'est égal à rien : écrire CASE WHEN colonne IS NULL. Sans "
        "ELSE, le CASE renvoie NULL (ignoré par SUM, mais qui change AVG "
        "et COUNT(colonne))",
        # grouping_sets
        "GROUP BY GROUPING SETS ((a, b), (a))  -- ajouter () pour le total "
        "général ; les colonnes non groupées valent NULL",
        "GROUP BY ROLLUP (a, b, c)  -- = GROUPING SETS ((a, b, c), (a, b), "
        "(a), ())",
        "GROUP BY CUBE (a, b)  -- = GROUPING SETS ((a, b), (a), (b), ()), "
        "2^n groupements",
        "GROUPING(colonne)  -- 1 si la colonne est agrégée (NULL de "
        "sous-total), 0 sinon",
    ],
    "example": [
        # stats
        "SELECT AVG(amount) FROM sales;",
        "SELECT STDDEV(amount) FROM sales;",
        "SELECT STDDEV_POP(amount) FROM sales;",
        "SELECT client_name, SUM(amount) AS total\n"
        "FROM sales\n"
        "GROUP BY client_name;",
        "SELECT COALESCE(bonus, 0) FROM employees;",
        "SELECT CAST(amount AS INTEGER) FROM sales;",
        # window_functions
        "SELECT client_name, amount,\n"
        "    ROW_NUMBER() OVER (ORDER BY amount DESC) AS rang\n"
        "FROM sales;",
        "SELECT client_name, amount,\n"
        "    RANK() OVER (ORDER BY amount DESC) AS rang\n"
        "FROM sales;",
        "SELECT client_name, amount,\n"
        "    DENSE_RANK() OVER (ORDER BY amount DESC) AS rang\n"
        "FROM sales;",
        "SELECT client_name, amount,\n"
        "    LAG(amount) OVER (ORDER BY amount) AS montant_precedent\n"
        "FROM sales;",
        "SELECT client_name, amount,\n"
        "    LEAD(amount) OVER (ORDER BY amount) AS montant_suivant\n"
        "FROM sales;",
        "SELECT client_name, amount,\n"
        "    SUM(amount) OVER (PARTITION BY client_name) AS total_client\n"
        "FROM sales;",
        # cte
        "WITH gros_clients AS (\n"
        "    SELECT client_name, SUM(amount) AS total\n"
        "    FROM sales\n"
        "    GROUP BY client_name\n"
        ")\n"
        "SELECT * FROM gros_clients\n"
        "WHERE total > 100;",
        "WITH totaux AS (\n"
        "    SELECT client_name, SUM(amount) AS total\n"
        "    FROM sales GROUP BY client_name\n"
        "),\n"
        "global AS (\n"
        "    SELECT SUM(total) AS grand_total FROM totaux\n"
        ")\n"
        "SELECT client_name, total / grand_total AS part\n"
        "FROM totaux CROSS JOIN global;",
        # joins
        "SELECT * FROM orders\n"
        "INNER JOIN customers USING (customer_id);",
        "SELECT * FROM customers\n"
        "LEFT JOIN orders USING (customer_id);",
        "SELECT * FROM orders\n"
        "FULL OUTER JOIN customers USING (customer_id);",
        "SELECT * FROM sizes\n"
        "CROSS JOIN trademarks;",
        "SELECT e.name AS employe, m.name AS manager\n"
        "FROM employees e\n"
        "JOIN employees m ON e.manager_id = m.id;",
        "SELECT c.customer_name\n"
        "FROM customers c\n"
        "LEFT JOIN orders o ON c.customer_id = o.customer_id\n"
        "WHERE o.order_id IS NULL;",
        # null_filtering
        "SELECT client_name, SUM(amount) AS total\n"
        "FROM sales\n"
        "WHERE amount > 0\n"
        "GROUP BY client_name\n"
        "HAVING SUM(amount) > 100;",
        "SELECT NULLIF(bonus, 0) FROM employees;",
        "SELECT * FROM employees WHERE bonus IS NULL;",
        "SELECT client_name, SUM(amount) AS total  -- 6. SELECT\n"
        "FROM sales                               -- 1. FROM\n"
        "WHERE amount > 0                         -- 3. WHERE\n"
        "GROUP BY client_name                     -- 4. GROUP BY\n"
        "HAVING SUM(amount) > 100                 -- 5. HAVING\n"
        "ORDER BY total DESC;                     -- 7. ORDER BY",
        # aggregates
        "SELECT COUNT(*), COUNT(bonus) FROM employees;",
        "SELECT DISTINCT client_name FROM sales;",
        "SELECT store_id, COUNT(DISTINCT product_name) AS nb_products\n"
        "FROM store_sales\n"
        "GROUP BY store_id;",
        # sets
        "SELECT client_name FROM sales_2024\n"
        "UNION\n"
        "SELECT client_name FROM sales_2025;",
        # dates
        "SELECT CURRENT_DATE;",
        "SELECT EXTRACT(YEAR FROM order_date) FROM orders;",
        "SELECT delivery_date - order_date AS jours_livraison FROM orders;",
        "SELECT order_date + INTERVAL '7 days' FROM orders;",
        "SELECT DATE_TRUNC('month', order_date) FROM orders;",
        # strings
        "SELECT first_name || ' ' || last_name FROM clients;",
        "SELECT SUBSTRING(client_name, 1, 3) FROM sales;",
        "SELECT UPPER(client_name), LOWER(client_name) FROM sales;",
        "SELECT TRIM('  Oussama  ');",
        "SELECT LENGTH(client_name) FROM sales;",
        "SELECT * FROM sales WHERE client_name LIKE 'J%';",
        # crud
        "INSERT INTO products (product_id, product_name, product_price)\n"
        "VALUES (102, 'Casque', 150);",
        "INSERT INTO sales_archive (client_name, amount)\n"
        "SELECT client_name, amount FROM sales WHERE amount >= 60;",
        "UPDATE products\n"
        "SET product_price = product_price + 50\n"
        "WHERE product_price > 100;",
        "DELETE FROM customers\n"
        "WHERE customer_id = 106;",
        # case_when
        "SELECT name, wage,\n"
        "    CASE\n"
        "        WHEN wage < 70000 THEN 'Junior'\n"
        "        WHEN wage < 90000 THEN 'Confirmed'\n"
        "        ELSE 'Senior'\n"
        "    END AS wage_band\n"
        "FROM wages;",
        "SELECT order_id,\n"
        "    CASE\n"
        "        WHEN discount_code IS NULL THEN 'no_code'\n"
        "        ELSE discount_code\n"
        "    END AS code_label\n"
        "FROM orders_discounts;",
        # grouping_sets
        "SELECT store_id, product_name, SUM(amount)\n"
        "FROM store_sales\n"
        "GROUP BY GROUPING SETS ((store_id, product_name), (store_id));",
        "SELECT year, region, department, SUM(population)\n"
        "FROM department_population\n"
        "GROUP BY ROLLUP (year, region, department);",
        "SELECT store_id, product_name, SUM(amount)\n"
        "FROM store_sales\n"
        "GROUP BY CUBE (store_id, product_name);",
        "SELECT\n"
        "    CASE WHEN GROUPING(discount_code) = 1 THEN 'TOTAL'\n"
        "         ELSE discount_code END AS label,\n"
        "    SUM(quantity)\n"
        "FROM orders_discounts\n"
        "GROUP BY ROLLUP (discount_code);",
    ],
}
flashcards_data["last_reviewed"] = ["1970-01-01"] * len(flashcards_data["card_name"])
flashcards_data["interval_step"] = [0] * len(flashcards_data["card_name"])
flashcards_df = pd.DataFrame(flashcards_data)
con.execute("CREATE TABLE IF NOT EXISTS flashcards AS SELECT * FROM flashcards_df")

# Rétrocompatibilité : la colonne "example" a été ajoutée après coup, une
# base créée avant n'a pas cette colonne (CREATE TABLE IF NOT EXISTS ne
# modifie pas un schéma déjà existant).
con.execute("ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS example VARCHAR")

# Même logique que pour memory_state : on n'ajoute que les cartes absentes,
# pour ne pas écraser la progression de révision des cartes déjà en place.
# Colonnes listées explicitement : dans une base créée avant l'ajout de
# "example", cette colonne est en DERNIÈRE position (ALTER TABLE), alors
# qu'elle précède last_reviewed dans flashcards_df.
con.execute("""
    INSERT INTO flashcards
        (theme, card_name, question, answer, example, last_reviewed, interval_step)
    SELECT n.theme, n.card_name, n.question, n.answer, n.example,
        n.last_reviewed, n.interval_step
    FROM flashcards_df n
    WHERE NOT EXISTS (
        SELECT 1 FROM flashcards m WHERE m.card_name = n.card_name
    )
""")

# Le contenu pédagogique (question/answer/example) peut évoluer pour une
# carte déjà existante : on le rafraîchit systématiquement, contrairement à
# last_reviewed/interval_step (progression de révision) qui ne sont jamais
# touchés une fois la carte créée.
con.execute("""
    UPDATE flashcards
    SET question = flashcards_df.question,
        answer = flashcards_df.answer,
        example = flashcards_df.example
    FROM flashcards_df
    WHERE flashcards.card_name = flashcards_df.card_name
""")

con.close()
