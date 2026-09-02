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

con.close()
