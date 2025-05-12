import sqlite3

# Connect to the database
conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

# Define default categories
default_categories = [
    {"idx": "boost", "title": "Boost Services"},
    {"idx": "unlock", "title": "Unlock Services"},
]

# Define default products
default_products = [
    {"idx": "gold_multi", "title": "Gold Multi", "body": "Service for Gold Multi", "photo": None, "price": 600000, "tag": "Boost Services"},
    {"idx": "gold_zombie", "title": "Gold Zombie", "body": "Service for Gold Zombie", "photo": None, "price": 700000, "tag": "Boost Services"},
    {"idx": "battle_pass", "title": "Battle Pass Unlock", "body": "Unlock Battle Pass", "photo": None, "price": 700000, "tag": "Unlock Services"},
]

# Verify categories
categories = cursor.execute('SELECT * FROM categories').fetchall()
if not categories:
    print("No categories found. Adding default categories...")
    for category in default_categories:
        cursor.execute('INSERT INTO categories (idx, title) VALUES (?, ?)', (category['idx'], category['title']))

# Verify products
products = cursor.execute('SELECT * FROM products').fetchall()
if not products:
    print("No products found. Adding default products...")
    for product in default_products:
        cursor.execute('INSERT INTO products (idx, title, body, photo, price, tag) VALUES (?, ?, ?, ?, ?, ?)',
                       (product['idx'], product['title'], product['body'], product['photo'], product['price'], product['tag']))

# Ensure products are linked to categories
for product in default_products:  # Iterate over default_products only (to ensure linking is correct)
    cursor.execute('UPDATE products SET tag = (SELECT title FROM categories WHERE title = ?) WHERE idx = ?', (product['tag'], product['idx']))

# Commit and close
conn.commit()
conn.close()
print("Database verification and updates complete.")