import mysql.connector
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME
from mysql.connector import Error

# Create a database connection
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

# Get a user by their phone number
def get_user_by_phone(phone_number):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE phone_number = %s"
    cursor.execute(query, (phone_number,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

# Get a product by its article number
def get_product_by_article(article_number):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM products WHERE article_number LIKE %s"
    cursor.execute(query, (article_number,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        columns = ["id", "store_id", "article_number", "metal_type", "product_type", "weight", "price_per_gram", "price", "min_price", "arrival_date"]
        product = dict(zip(columns, result))
        return product
    else:
        return None


# Get a store by its ID
def get_store_by_id(store_id):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM stores WHERE id = %s"
    cursor.execute(query, (store_id,))
    store = cursor.fetchone()
    cursor.close()
    connection.close()
    return store

# Record a sale
def record_sale(product_id, store_id, user_id, sale_price, payment_type):
    connection = create_connection()
    cursor = connection.cursor()
    query = "INSERT INTO sales (product_id, store_id, user_id, sale_date, sold_price, payment_type) VALUES (%s, %s, %s, NOW(), %s, %s)"
    cursor.execute(query, (product_id, store_id, user_id, sale_price, payment_type))
    connection.commit()
    cursor.close()
    connection.close()

# Get the minimum price of a product
def get_min_price(product):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT min_price FROM products WHERE id = %s"
    cursor.execute(query, (product[0],))
    min_price = None
    result = cursor.fetchone()
    if result:
        min_price = result[0]
    cursor.close()
    connection.close()
    return min_price

# Get the maximum price of a product