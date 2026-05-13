def create_tables(conn):
# Assume one-to-many relationship. One product may have multiple competitor
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id_diy TEXT PRIMARY KEY,
        title TEXT,
        brand TEXT,
        category TEXT,
        segment TEXT,
        collection TEXT,
        product_type TEXT,
        price REAL,
        price_per_unit REAL,
        final_unit TEXT,
        image_url TEXT,
        product_url TEXT
    )
    """)

#
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT,
        competitor_vendor TEXT,
        competitor_title TEXT,
        competitor_price REAL,
        competitor_price_per_unit REAL,
        matching_score REAL,
        image_similarity REAL,
        exact_match REAL,
        brand_match REAL,
        scent_match REAL,
        competitor_url TEXT,
        competitor_image TEXT,
        FOREIGN KEY (product_id) REFERENCES products(product_id_diy)
    )
    """)

    conn.commit()