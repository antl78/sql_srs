import io
import pandas as pd
import duckdb

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

# ----------------------------------------
# EXERCISES LIST
# ----------------------------------------
data = {
    "theme": ["cross_joins", "cross_joins", "inner_joins", "inner_joins", "inner_joins"],
    "exercise_name": [
        "beverages_and_food",
        "sizes_and_trademarks",
        "orders_and_order_details",
        "orders_details_and_customers",
        "orders_customers_and_products",
    ],
    "statement": [
        "Associe chaque boisson à chaque plat pour générer toutes les combinaisons "
        "possibles (produit cartésien).",
        "Associe chaque taille à chaque marque pour générer toutes les combinaisons "
        "possibles (produit cartésien).",
        "Pour chaque commande, retrouve le produit commandé et la quantité en associant "
        "les commandes (df_orders) à leurs détails (df_order_details) via order_id.",
        "Ajoute le nom du client à chaque commande détaillée, en associant "
        "detailed_order (résultat de l'exercice précédent) à df_customers via "
        "customer_id.",
        "Ajoute le nom et le prix du produit à chaque commande, en associant "
        "order_client (résultat de l'exercice précédent) à df_products via "
        "product_id.",
    ],
    "tables": [
        ["beverages", "food_items"],
        ["sizes", "trademarks"],
        ["df_orders", "df_order_details"],
        ["df_customers", "detailed_order"],
        ["order_client", "df_products"],
    ],
    "last_reviewed": ["1980-01-01", "1970-01-01", "1970-01-01", "1970-01-01", "1970-01-01"],
    # Position dans l'échelle de révision REVIEW_INTERVALS (app.py) : avance
    # d'un cran à chaque succès, retombe à 0 au premier échec.
    "interval_step": [0, 0, 0, 0, 0],
}
memory_state_df = pd.DataFrame(data)
con.execute("CREATE TABLE IF NOT EXISTS memory_state AS SELECT * FROM memory_state_df")


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
df_orders = pd.DataFrame(orders_data)
con.execute("CREATE TABLE IF NOT EXISTS df_orders AS SELECT * FROM df_orders")

customers_data = {
    "customer_id": [101, 102, 103, 104, 105, 106],
    "customer_name": ["Toufik", "Daniel", "Tancrède", "Kaouter", "Jean-Nicolas", "David"],
}
df_customers = pd.DataFrame(customers_data)
con.execute("CREATE TABLE IF NOT EXISTS df_customers AS SELECT * FROM df_customers")

p_names = ["Laptop", "Ipad", "Livre", "Petitos"]
products_data = {
    "product_id": [101, 103, 104, 105],
    "product_name": p_names,
    "product_price": [800, 400, 30, 2],
}
df_products = pd.DataFrame(products_data)
con.execute("CREATE TABLE IF NOT EXISTS df_products AS SELECT * FROM df_products")

order_details_data = {
    "order_id": [1, 2, 3, 4, 5],
    "product_id": [102, 104, 101, 103, 105],
    "quantity": [2, 1, 3, 2, 1],
}
df_order_details = pd.DataFrame(order_details_data)
con.execute("CREATE TABLE IF NOT EXISTS df_order_details AS SELECT * FROM df_order_details")

# Table "detailed_order" : résultat attendu de l'exercice 1 (df_orders INNER JOIN
# df_order_details), matérialisée pour servir de point de départ à l'exercice 2
# sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS detailed_order AS
    SELECT * FROM df_orders
    INNER JOIN df_order_details
    USING (order_id)
""")

# Table "order_client" : résultat attendu de l'exercice 2 (df_customers INNER JOIN
# detailed_order), matérialisée pour servir de point de départ à l'exercice 3
# sans avoir besoin d'un CTE.
con.execute("""
    CREATE TABLE IF NOT EXISTS order_client AS
    SELECT df_customers.customer_id,
        customer_name,
        order_id,
        product_id,
        quantity
    FROM df_customers
    INNER JOIN detailed_order
    ON df_customers.customer_id = detailed_order.customer_id
""")

con.close()
