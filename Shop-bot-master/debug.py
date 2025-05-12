def print_db_contents(db):
    print("Categories:")
    for row in db.fetchall('SELECT * FROM categories'):
        print(row)
    
    print("\nProducts:")
    for row in db.fetchall('SELECT * FROM products'):
        print(row)