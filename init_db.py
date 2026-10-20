import io
import random
from datetime import date, timedelta

import pandas as pd
import duckdb

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

# Base de CONTENU uniquement (exercices, tables, mémocards) : la progression
# de révision vit dans data/progress.duckdb, gérée par app.py.
# Ancien nom de la table des exercices (quand elle contenait aussi la
# progression) : renommée pour qu'une base existante soit mise à jour.
legacy_tables = [
    row[0]
    for row in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name IN ('memory_state', 'exercises')"
    ).fetchall()
]
if legacy_tables == ["memory_state"]:
    con.execute("ALTER TABLE memory_state RENAME TO exercises")

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
        # Niveau 4 : CASE WHEN dans un agrégat, dates
        "conditional_aggregation", "conditional_aggregation",
        "conditional_aggregation", "conditional_aggregation",
        "dates", "dates", "dates", "dates", "dates",
        # Niveau 5 : window functions
        "window_functions", "window_functions", "window_functions",
        "window_functions", "window_functions", "window_functions",
        "ranking", "ranking", "ranking",
        "lag_lead", "lag_lead", "lag_lead", "lag_lead",
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
        "wine_share_per_store",
        "it_vs_other_payroll",
        "store_product_pivot",
        "well_paid_rate_per_department",
        "monthly_revenue",
        "revenue_per_weekday",
        "clients_long_purchase_span",
        "monthly_revenue_pivot_per_client",
        "visits_vs_previous_week",
        "visits_below_monthly_average",
        "wage_vs_department_average",
        "running_revenue_per_client",
        "cumulative_revenue_end_of_day",
        "daily_sales_full_3_day_average",
        "visitors_last_7_calendar_days",
        "sales_amount_rankings",
        "top_2_sales_per_client",
        "second_highest_wage_per_department",
        "days_between_consecutive_purchases",
        "daily_sales_day_over_day",
        "gaps_before_next_visit_record",
        "high_traffic_streaks",
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
        # conditional_aggregation
        "Pour chaque magasin de store_sales, affiche le montant vendu en "
        "vin ('wine'), le montant total, et la part du vin dans le total en "
        "pourcentage arrondi à 2 décimales. Une seule requête GROUP BY, sans "
        "CTE ni FILTER (pas portable). Colonnes : store_id, montant vin, "
        "montant total, part en %.",
        "En une seule ligne, affiche la masse salariale du département IT, "
        "celle de tous les autres départements réunis, et la part de l'IT "
        "dans la masse salariale totale en pourcentage arrondi à 2 "
        "décimales. Attention à la division entière sur d'autres SGBD que "
        "DuckDB.",
        "Pivote store_sales : une ligne par magasin, une colonne par produit "
        "(redbull, chips, wine, icecream) contenant le montant total vendu. "
        "Un produit jamais vendu dans un magasin doit valoir 0, pas NULL. "
        "Sans PIVOT (pas portable).",
        "Pour chaque département de wages, affiche l'effectif et le "
        "pourcentage de salariés payés au moins 70 000, arrondi à 2 "
        "décimales (ex : 75 pour 75 %). Une seule requête, sans CTE ni "
        "sous-requête.",
        # dates
        "Affiche, pour chaque mois, le nombre de ventes et le chiffre "
        "d'affaires de sales. Le mois est une date : le 1er du mois "
        "(ex : 2026-02-01).",
        "Affiche le nombre de ventes et le chiffre d'affaires de sales par "
        "jour de la semaine, identifié par son numéro EXTRACT(DOW ...) "
        "(0 = dimanche, 6 = samedi). Colonnes : numéro du jour, nombre de "
        "ventes, CA.",
        "Pour chaque client de sales, affiche la date de sa première vente, "
        "celle de sa dernière vente et le nombre de jours entre les deux. "
        "Ne garde que les clients pour qui cet écart est d'au moins 60 "
        "jours.",
        "Pivote le chiffre d'affaires de sales par mois : une ligne par "
        "client, une colonne par mois (janvier, février, mars 2026). Un mois "
        "sans vente vaut 0. Colonnes : client_name, puis les trois mois dans "
        "l'ordre.",
        "Pour chaque jour de sensor_visits, affiche le nombre de visiteurs, "
        "celui du même jour de la semaine précédente (date - 7 jours, NULL "
        "s'il n'y a pas de relevé ce jour-là) et la différence entre les "
        "deux. Attention : il n'y a pas de relevé le dimanche, donc ne "
        "suppose pas qu'une semaine = un nombre fixe de lignes, travaille "
        "sur les dates. Colonnes : visit_date, visitor_count, valeur J-7, "
        "différence.",
        # window_functions
        "Dans sensor_visits, affiche les jours où la fréquentation est "
        "inférieure de plus de 10 % à la moyenne du mois (visitor_count < "
        "90 % de la moyenne de tous les relevés). Colonnes : visit_date, "
        "visitor_count, moyenne du mois arrondie à 2 décimales. Calcule la "
        "moyenne avec une window function, sans GROUP BY ni jointure.",
        "Pour chaque salarié de wages, affiche name, department, wage, le "
        "salaire moyen de son département et l'écart entre son salaire et "
        "cette moyenne (les deux arrondis à 2 décimales). Toutes les lignes "
        "sont conservées : pas de GROUP BY.",
        "Pour chaque vente de sales, affiche client_name, sale_date, amount "
        "et le chiffre d'affaires cumulé du client à cette date (somme de "
        "ses ventes depuis la première, celle du jour comprise).",
        "Pour chaque vente de sales, affiche sale_date, client_name, amount "
        "et le CA cumulé de toutes les ventes à la fin de la journée de "
        "cette vente : deux ventes du même jour ont donc le même cumul, qui "
        "inclut les deux. Attention, plusieurs ventes partagent une date.",
        "Dans daily_sales, affiche pour chaque jour sale_date, daily_sales "
        "et la moyenne mobile sur 3 jours (le jour et les 2 précédents), "
        "arrondie à 2 décimales. Les 2 premiers jours n'ont pas 3 jours "
        "d'historique : la moyenne doit y valoir NULL, pas une moyenne sur "
        "1 ou 2 jours.",
        "Dans sensor_visits, affiche pour chaque relevé visit_date, "
        "visitor_count et le total des visiteurs sur les 7 jours "
        "calendaires qui se terminent ce jour-là (de J-6 à J inclus). Il "
        "n'y a pas de relevé le dimanche.",
        # ranking
        "Classe les ventes de sales par montant décroissant. Affiche "
        "client_name, sale_date, amount, puis trois classements : un numéro "
        "unique (à montant égal, la vente la plus ancienne passe devant), "
        "un rang avec trous en cas d'ex-aequo (1, 1, 3) et un rang sans "
        "trou (1, 1, 2).",
        "Pour chaque client de sales, affiche ses 2 plus grosses ventes "
        "(exactement 2 lignes par client) : client_name, sale_date, amount. "
        "À montant égal, garde la vente la plus ancienne.",
        "Pour chaque département de wages, affiche le salarié qui a le 2e "
        "salaire le plus élevé : department, name, wage. Un département "
        "d'un seul salarié n'apparaît pas. Sans LIMIT / OFFSET : il faut "
        "un résultat par département.",
        # lag_lead
        "Pour chaque vente de sales, affiche client_name, sale_date, la "
        "date de l'achat précédent du même client et le nombre de jours "
        "écoulés depuis (NULL pour son premier achat).",
        "Dans daily_sales, affiche pour chaque jour sale_date, daily_sales, "
        "les ventes de la veille, la variation (jour - veille) et la "
        "variation en % des ventes de la veille, arrondie à 2 décimales "
        "(ex : -83.33). Le premier jour n'a pas de veille : NULL. Attention "
        "à la division entière sur d'autres SGBD que DuckDB.",
        "Repère les trous dans sensor_visits : affiche les relevés suivis "
        "d'au moins un jour sans relevé, avec visit_date, la date du relevé "
        "suivant et le nombre de jours qui les séparent.",
        "Dans sensor_visits, trouve les séries de jours calendaires "
        "consécutifs où visitor_count est d'au moins 5000. Pour chaque "
        "série d'au moins 2 jours, affiche la date de début, la date de fin "
        "et le nombre de jours.",
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
        # conditional_aggregation
        ["store_sales"],
        ["wages"],
        ["store_sales"],
        ["wages"],
        # dates
        ["sales"],
        ["sales"],
        ["sales"],
        ["sales"],
        ["sensor_visits"],
        # window_functions
        ["sensor_visits"],
        ["wages"],
        ["sales"],
        ["sales"],
        ["daily_sales"],
        ["sensor_visits"],
        # ranking
        ["sales"],
        ["sales"],
        ["wages"],
        # lag_lead
        ["sales"],
        ["daily_sales"],
        ["sensor_visits"],
        ["sensor_visits"],
    ],
}
exercises_df = pd.DataFrame(data)
con.execute("CREATE TABLE IF NOT EXISTS exercises AS SELECT * FROM exercises_df")

# Si la base existe déjà, on ajoute seulement les exercices absents (l'ordre
# d'insertion sert d'ordre de passage dans app.py, cf. EXERCISE_STATE_CTE).
con.execute("""
    INSERT INTO exercises (theme, exercise_name, statement, tables)
    SELECT n.theme, n.exercise_name, n.statement, n.tables
    FROM exercises_df AS n
    ANTI JOIN exercises AS m USING (exercise_name)
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

# Niveau 4 : sale_date ajoutée pour les exercices sur les dates. Générateur
# dédié (random.Random) pour ne pas décaler les tirages ci-dessus : chaque
# vente reçoit une date du 1er trimestre 2026 (reproductible).
dates_rng = random.Random(2026)
sales_data = {
    "client_name": [clients[i % len(clients)] for i in range(len(ventes))],
    "amount": ventes,
    "sale_date": [
        date(2026, 1, 1) + timedelta(days=dates_rng.randrange(90))
        for _ in ventes
    ],
}
# Nommé sales_df (et non sales) : dans "SELECT ... FROM sales", DuckDB lit la
# table sales si elle existe déjà, et ne regarde le DataFrame Python qu'à
# défaut.
sales_df = pd.DataFrame(sales_data)
SALES_SELECT = (
    "SELECT client_name, amount, CAST(sale_date AS DATE) AS sale_date "
    "FROM sales_df"
)
con.execute(f"CREATE TABLE IF NOT EXISTS sales AS {SALES_SELECT}")

# Migration d'une base créée avant le niveau 4 (sales sans sale_date) : la
# table est recréée, ce qui est sans risque car elle ne contient aucune
# progression (celle-ci est dans data/progress.duckdb).
sales_has_date = con.execute("""
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'sale_date'
""").fetchone()[0]
if not sales_has_date:
    con.execute(f"CREATE OR REPLACE TABLE sales AS {SALES_SELECT}")

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
# LEVEL 4 : CASE WHEN DANS UN AGRÉGAT, DATES
# ----------------------------------------
# Les exercices réutilisent store_sales / wages (niveau 3) et sales (avec
# sale_date, voir plus haut).

# sensor_visits (cours : capteurs). 01 -> 23/08 = valeurs du cours, 24 ->
# 31/08 synthétique sauf le 30 (5500, visible dans le cours). Pas de
# relevé le dimanche : "7 jours avant" n'est donc pas "7 lignes avant".
# Resservira au niveau 5 (window functions).
con.execute("""
    CREATE TABLE IF NOT EXISTS sensor_visits AS
    SELECT CAST(visit_date AS DATE) AS visit_date, sensor_id, visitor_count
    FROM (VALUES
        ('2023-08-01', 'porte_a', 4200), ('2023-08-02', 'porte_a', 5300),
        ('2023-08-03', 'porte_a', 4400), ('2023-08-04', 'porte_a', 5500),
        ('2023-08-05', 'porte_a', 6000), ('2023-08-07', 'porte_a', 4200),
        ('2023-08-08', 'porte_a', 4700), ('2023-08-09', 'porte_a', 5300),
        ('2023-08-10', 'porte_a', 4400), ('2023-08-11', 'porte_a', 5500),
        ('2023-08-12', 'porte_a', 6000), ('2023-08-14', 'porte_a', 3900),
        ('2023-08-15', 'porte_a', 4200), ('2023-08-16', 'porte_a', 4700),
        ('2023-08-17', 'porte_a', 3600), ('2023-08-18', 'porte_a', 5000),
        ('2023-08-19', 'porte_a', 5500), ('2023-08-21', 'porte_a', 4300),
        ('2023-08-22', 'porte_a', 4900), ('2023-08-23', 'porte_a', 5500),
        ('2023-08-24', 'porte_a', 4600), ('2023-08-25', 'porte_a', 5200),
        ('2023-08-26', 'porte_a', 5800), ('2023-08-28', 'porte_a', 4100),
        ('2023-08-29', 'porte_a', 4500), ('2023-08-30', 'porte_a', 5500),
        ('2023-08-31', 'porte_a', 4800)
    ) AS t(visit_date, sensor_id, visitor_count)
""")

# ----------------------------------------
# LEVEL 5 : WINDOW FUNCTIONS
# ----------------------------------------
# Les exercices réutilisent sensor_visits, wages et sales. Dans sales, chaque
# montant apparaît deux fois (liste doublée) : égalités naturelles pour
# RANK / DENSE_RANK / ROW_NUMBER. Deux dates (10/02 et 04/03) portent deux
# ventes : piège ROWS vs RANGE sur un cumul par date.

# daily_sales (cours : df ROWS BETWEEN). 01 -> 07/09 = valeurs du cours,
# 08 -> 10/09 synthétique.
con.execute("""
    CREATE TABLE IF NOT EXISTS daily_sales AS
    SELECT CAST(sale_date AS DATE) AS sale_date, daily_sales
    FROM (VALUES
        ('2023-09-01', 6000), ('2023-09-02', 1000), ('2023-09-03', 1000),
        ('2023-09-04', 6000), ('2023-09-05', 3000), ('2023-09-06', 2000),
        ('2023-09-07', 2000), ('2023-09-08', 4000), ('2023-09-09', 5000),
        ('2023-09-10', 1500)
    ) AS t(sale_date, daily_sales)
""")

# ----------------------------------------
# FLASHCARDS (memocards) - fonctions SQL a retenir
# ----------------------------------------
# Contrairement aux exercices ci-dessus (requête à écrire, comparée à une
# solution), une flashcard est une simple paire question/réponse pour la
# mémorisation de syntaxe, accompagnée d'un exemple de requête concret
# (colonne "example", affiché sous la réponse dans l'app) pour visualiser
# la syntaxe en contexte. Table séparée de exercises : pas de notion de
# "tables" utilisées. Pas encore de répétition espacée sur les cartes ; le
# moment venu, leur progression ira dans data/progress.duckdb, comme celle
# des exercices.
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
        + ["conditional_aggregation"] * 4
        + ["dates"] * 2
        + ["window_functions"] * 8
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
        # conditional_aggregation
        "sum_case_when",
        "filter_clause",
        "conditional_rate",
        "integer_division",
        # dates (suite)
        "extract_dow",
        "same_day_previous_week",
        # window_functions (suite)
        "over_empty",
        "running_total",
        "rows_between",
        "range_interval",
        "filter_on_window",
        "top_n_per_group",
        "window_after_group_by",
        "gaps_and_islands",
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
        # conditional_aggregation
        "Comment sommer seulement les lignes qui vérifient une condition, "
        "dans un GROUP BY (ex : pivot manuel, une colonne par produit) ?",
        "Quelle syntaxe plus courte (mais non portable) remplace "
        "SUM(CASE WHEN cond THEN x END) ?",
        "Comment calculer le pourcentage de lignes qui vérifient une "
        "condition (taux de conversion, part de clients...) ?",
        "Pourquoi SUM(a) / SUM(b) peut renvoyer 0 sur Postgres ou SQL "
        "Server, et comment l'éviter ?",
        # dates (suite)
        "Comment obtenir le jour de la semaine d'une date, et quelle est "
        "la convention de numérotation ?",
        "Comment comparer chaque jour au même jour de la semaine précédente "
        "quand il manque des dates (pas de relevé certains jours) ?",
        # window_functions (suite)
        "Comment afficher sur chaque ligne un agrégat calculé sur toute la "
        "table (ex : total général), sans réduire le nombre de lignes ?",
        "Comment calculer un cumul progressif, et quelle est la fenêtre "
        "par défaut quand on met seulement ORDER BY dans OVER ?",
        "Comment calculer une moyenne mobile sur les 3 dernières lignes ?",
        "Comment définir une fenêtre de 7 jours calendaires quand il "
        "manque des dates ?",
        "Pourquoi ne peut-on pas filtrer sur une window function dans le "
        "WHERE, et comment faire ?",
        "Comment garder les N premières lignes de chaque groupe (ex : les 2 "
        "plus grosses ventes de chaque client) ?",
        "Comment calculer la part de chaque groupe dans le total, dans la "
        "même requête que le GROUP BY ?",
        "Comment regrouper des jours consécutifs en séries (gaps and "
        "islands) ?",
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
        # conditional_aggregation
        "SUM(CASE WHEN condition THEN colonne ELSE 0 END)  -- ELSE 0 pour "
        "obtenir 0 au lieu de NULL quand aucune ligne ne correspond",
        "SUM(colonne) FILTER (WHERE condition)  -- Postgres/DuckDB "
        "seulement ; en entretien, préférer CASE WHEN",
        "AVG(CASE WHEN condition THEN 1.0 ELSE 0 END)  -- le ELSE 0 est "
        "indispensable : sans lui, AVG ignore les NULL et renvoie 1",
        "Division de deux entiers = division entière sur Postgres / SQL "
        "Server : écrire SUM(a) * 1.0 / SUM(b) ou CAST(... AS DECIMAL). "
        "DuckDB fait déjà une division décimale",
        "EXTRACT(DOW FROM colonne)  -- 0 = dimanche … 6 = samedi "
        "(Postgres/DuckDB) ; EXTRACT(ISODOW ...) : 1 = lundi … 7 = dimanche",
        "Self join sur la date : LEFT JOIN t prev ON prev.d = cur.d - "
        "INTERVAL '7 days'  -- LAG(x, 7) suppose une ligne par jour, sans "
        "trou",
        # window_functions (suite)
        "SUM(colonne) OVER ()  -- OVER vide = toute la table comme "
        "fenêtre, résultat répété sur chaque ligne",
        "SUM(x) OVER (ORDER BY d)  -- défaut : RANGE BETWEEN UNBOUNDED "
        "PRECEDING AND CURRENT ROW, les ex-aequo sur d sont cumulés "
        "ensemble ; ROWS UNBOUNDED PRECEDING pour un cumul ligne à ligne",
        "AVG(x) OVER (ORDER BY d ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)  "
        "-- aux bords la fenêtre est plus petite : tester COUNT(*) OVER "
        "(même fenêtre) = 3 pour n'afficher que les fenêtres complètes",
        "SUM(x) OVER (ORDER BY d RANGE BETWEEN INTERVAL '6 days' PRECEDING "
        "AND CURRENT ROW)  -- RANGE porte sur les valeurs de d, ROWS sur le "
        "nombre de lignes",
        "Les window functions sont calculées au moment du SELECT, après "
        "WHERE / GROUP BY / HAVING : les calculer dans une CTE, puis "
        "filtrer dessus. QUALIFY (DuckDB, Snowflake, BigQuery) le fait "
        "directement, mais n'est pas portable",
        "CTE avec ROW_NUMBER() OVER (PARTITION BY groupe ORDER BY x DESC) "
        "AS rn, puis WHERE rn <= N  -- RANK / DENSE_RANK si tous les "
        "ex-aequo doivent être gardés",
        "SUM(SUM(x)) OVER ()  -- la window function s'applique après le "
        "GROUP BY, sur les lignes déjà agrégées",
        "d - ROW_NUMBER() OVER (ORDER BY d) * INTERVAL '1 day' est "
        "constant sur une série de jours consécutifs : GROUP BY sur cette "
        "clé, puis MIN(d), MAX(d), COUNT(*)",
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
        # conditional_aggregation
        "SELECT store_id,\n"
        "    SUM(CASE WHEN product_name = 'chips' THEN amount ELSE 0 END) AS chips,\n"
        "    SUM(CASE WHEN product_name = 'wine' THEN amount ELSE 0 END) AS wine\n"
        "FROM store_sales\n"
        "GROUP BY store_id;",
        "SELECT department,\n"
        "    COUNT(*) FILTER (WHERE wage >= 80000) AS high_wages\n"
        "FROM wages\n"
        "GROUP BY department;",
        "SELECT department,\n"
        "    AVG(CASE WHEN wage >= 80000 THEN 1.0 ELSE 0 END) AS high_wage_rate\n"
        "FROM wages\n"
        "GROUP BY department;",
        "SELECT store_id,\n"
        "    SUM(CASE WHEN product_name = 'wine' THEN amount END) * 1.0\n"
        "        / SUM(amount) AS wine_share\n"
        "FROM store_sales\n"
        "GROUP BY store_id;",
        "SELECT EXTRACT(DOW FROM sale_date) AS weekday, COUNT(*)\n"
        "FROM sales\n"
        "GROUP BY EXTRACT(DOW FROM sale_date);",
        "SELECT cur.visit_date, cur.visitor_count,\n"
        "    prev.visitor_count AS previous_week\n"
        "FROM sensor_visits cur\n"
        "LEFT JOIN sensor_visits prev\n"
        "    ON prev.visit_date = cur.visit_date - INTERVAL '7 days';",
        # window_functions (suite)
        "SELECT client_name, amount,\n"
        "    amount * 100.0 / SUM(amount) OVER () AS pct_of_total\n"
        "FROM sales;",
        "SELECT sale_date, amount,\n"
        "    SUM(amount) OVER (ORDER BY sale_date) AS cumulative_revenue\n"
        "FROM sales;",
        "SELECT sale_date, daily_sales,\n"
        "    AVG(daily_sales) OVER (\n"
        "        ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW\n"
        "    ) AS moving_avg_3\n"
        "FROM daily_sales;",
        "SELECT visit_date,\n"
        "    SUM(visitor_count) OVER (\n"
        "        ORDER BY visit_date\n"
        "        RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW\n"
        "    ) AS last_7_days\n"
        "FROM sensor_visits;",
        "WITH v AS (\n"
        "    SELECT visit_date, visitor_count,\n"
        "        AVG(visitor_count) OVER () AS avg_count\n"
        "    FROM sensor_visits\n"
        ")\n"
        "SELECT * FROM v WHERE visitor_count < avg_count;",
        "WITH ranked AS (\n"
        "    SELECT client_name, amount,\n"
        "        ROW_NUMBER() OVER (\n"
        "            PARTITION BY client_name ORDER BY amount DESC\n"
        "        ) AS rn\n"
        "    FROM sales\n"
        ")\n"
        "SELECT * FROM ranked WHERE rn <= 2;",
        "SELECT department, SUM(wage) AS payroll,\n"
        "    SUM(wage) * 100.0 / SUM(SUM(wage)) OVER () AS pct_of_total\n"
        "FROM wages\n"
        "GROUP BY department;",
        "WITH s AS (\n"
        "    SELECT visit_date,\n"
        "        visit_date - ROW_NUMBER() OVER (ORDER BY visit_date)\n"
        "            * INTERVAL '1 day' AS streak_key\n"
        "    FROM sensor_visits\n"
        ")\n"
        "SELECT MIN(visit_date), MAX(visit_date), COUNT(*)\n"
        "FROM s GROUP BY streak_key;",
    ],
}
flashcards_df = pd.DataFrame(flashcards_data)
con.execute("CREATE TABLE IF NOT EXISTS flashcards AS SELECT * FROM flashcards_df")

# Rétrocompatibilité : la colonne "example" a été ajoutée après coup, une
# base créée avant n'a pas cette colonne (CREATE TABLE IF NOT EXISTS ne
# modifie pas un schéma déjà existant).
con.execute("ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS example VARCHAR")

# Même logique que pour exercises : on n'ajoute que les cartes absentes.
# Colonnes listées explicitement : dans une base créée avant l'ajout de
# "example", cette colonne est en DERNIÈRE position (ALTER TABLE).
con.execute("""
    INSERT INTO flashcards (theme, card_name, question, answer, example)
    SELECT n.theme, n.card_name, n.question, n.answer, n.example
    FROM flashcards_df AS n
    ANTI JOIN flashcards AS m USING (card_name)
""")

# Le contenu pédagogique (question/answer/example) peut évoluer pour une
# carte déjà existante : on le rafraîchit systématiquement.
con.execute("""
    UPDATE flashcards
    SET question = flashcards_df.question,
        answer = flashcards_df.answer,
        example = flashcards_df.example
    FROM flashcards_df
    WHERE flashcards.card_name = flashcards_df.card_name
""")

con.close()
