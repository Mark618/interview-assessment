from app.database.db import get_connection

def build_filters(category=None, segment=None, collection=None, product_type=None):
    filters = []
    params = []

    if category:
        filters.append("p.category = ?")
        params.append(category)
    if segment:
        filters.append("p.segment = ?")
        params.append(segment)
    if collection:
        filters.append("p.collection = ?")
        params.append(collection)
    if product_type:
        filters.append("p.product_type = ?")
        params.append(product_type)
        
    where_clause = " WHERE " + " AND ".join(filters) if filters else ""
    return where_clause, params

def get_overview_metrics(category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filters(category, segment, collection, product_type)
    result = {}

    # 1. Total Products
    cursor.execute(f"SELECT COUNT(*) FROM products p {where_clause}", params)
    result["total_products"] = cursor.fetchone()[0]

    # 2. Total Competitor Listings
    cursor.execute(f"SELECT COUNT(DISTINCT competitor_title) FROM competitor_prices c JOIN products p ON p.product_id_diy = c.product_id {where_clause}", params)
    result["total_competitor_listings"] = cursor.fetchone()[0]

    # 3. Average Price Index
    cursor.execute(f"""SELECT AVG(CASE 
                                    WHEN p.price = 0 THEN NULL
                                    ELSE p.price / c.competitor_price
                                END) 
                   FROM competitor_prices c JOIN products p ON p.product_id_diy = c.product_id {where_clause}""", params)
    result["avg_price_index"] = cursor.fetchone()[0]

    # 4. Overpriced Count
    if where_clause:
        temp_keywords = "AND"
    else:
        temp_keywords = "WHERE"
    overprice_cond = f"{temp_keywords} (CASE WHEN p.price = 0 THEN NULL ELSE p.price / c.competitor_price END) > 1.10"
    cursor.execute(f"SELECT COUNT(*) FROM competitor_prices c JOIN products p ON p.product_id_diy = c.product_id {where_clause} {overprice_cond}", params)
    result["overpriced_products"] = cursor.fetchone()[0]

    conn.close()
    return result

def get_top_overpriced_products(limit=20, category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)
    
    # Add pricing condition
    if where_clause:
        temp_keywords = "AND"
    else:
        temp_keywords = "WHERE"
    pricing_filter = f"{temp_keywords} (CASE WHEN p.price = 0 THEN NULL ELSE p.price / c.competitor_price END) > 1.10"

    query = f"""
    SELECT
        p.title, p.brand, p.category, p.price AS our_price,
        c.competitor_vendor, c.competitor_price,
        CASE 
            WHEN p.price = 0 THEN NULL
        ELSE p.price / c.competitor_price
        END AS price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    {where_clause} {pricing_filter}
    ORDER BY price_index DESC LIMIT ?
    """
    
    cursor.execute(query, params + [limit])
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_competitor_price_analysis(category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)

    query = f"""
    SELECT
        c.competitor_vendor,
        COUNT(*) as listings,
        AVG(CASE 
            WHEN p.price = 0 THEN NULL
            ELSE p.price / c.competitor_price
        END) as avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    {where_clause}
    GROUP BY c.competitor_vendor
    ORDER BY avg_price_index DESC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_category_price_analysis():
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT
        p.category,
        COUNT(*) as listings,
        AVG(CASE 
                WHEN p.price = 0 THEN NULL
                ELSE p.price / c.competitor_price
            END) as avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    GROUP BY p.category
    ORDER BY avg_price_index DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_segment_price_analysis():
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT
        p.segment,
        COUNT(*) as listings,
        AVG(CASE 
                WHEN p.price = 0 THEN NULL
                ELSE p.price / c.competitor_price
            END) as avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    GROUP BY p.segment
    ORDER BY avg_price_index DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_collection_price_analysis():
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT
        p.collection,
        COUNT(*) as listings,
        AVG(CASE 
                WHEN p.price = 0 THEN NULL
                ELSE p.price / c.competitor_price
            END) as avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    GROUP BY p.collection
    ORDER BY avg_price_index DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_prod_type_price_analysis():
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
    SELECT
        p.product_type,
        COUNT(*) as listings,
        AVG(CASE 
                WHEN p.price = 0 THEN NULL
                ELSE p.price / c.competitor_price
            END) as avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    GROUP BY p.product_type
    ORDER BY avg_price_index DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_price_index_distribution(category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)
    
    # Handle the null check
    if where_clause:
        temp_keywords = "AND"
    else:
        temp_keywords = "WHERE"
    null_check = f" {temp_keywords} (CASE WHEN p.price = 0 THEN NULL ELSE p.price / c.competitor_price END) IS NOT NULL"

    query = f"""
    SELECT CASE 
            WHEN p.price = 0 THEN NULL
        ELSE p.price / c.competitor_price
        END AS price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    {where_clause} {null_check}
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_product_competitor_prices(product_id):
    # No dynamic filters needed here as it is a specific product lookup
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        p.title, p.price AS our_price,
        c.competitor_vendor, c.competitor_price, c.price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    WHERE p.product_id_diy = ?
    """

    cursor.execute(query, (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_priority_repricing_products(limit=20, category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)

    query = f"""
    SELECT
        p.product_id_diy, p.title, p.brand, p.category, p.price AS our_price,
        COUNT(c.id) AS competitor_count,
        AVG(c.price_index) AS avg_price_index
    FROM competitor_prices c
    JOIN products p ON p.product_id_diy = c.product_id
    {where_clause}
    GROUP BY p.product_id_diy
    HAVING avg_price_index > 1.10
    ORDER BY avg_price_index DESC
    LIMIT ?
    """

    cursor.execute(query, params + [limit])
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_filter_values(category=None, segment=None, collection=None, product_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)

    filters = {}

    # Use a single query with GROUP BY for each field
    for field in ["category", "segment", "collection", "product_type"]:
        query = f"SELECT {field} FROM products p"
        if where_clause:
            query += " " + where_clause
        query += f" GROUP BY {field}"
        cursor.execute(query, params)
        filters[f"{field}s"] = [row[0] for row in cursor.fetchall() if row[0] is not None]

    conn.close()
    return filters


def get_buyer_products(
    search=None,
    category=None,
    segment=None,
    collection=None,
    product_type=None,
    limit=50
):
    conn = get_connection()
    cursor = conn.cursor()

    where_clause, params = build_filters(category, segment, collection, product_type)

    # Search condition
    search_clause = ""
    if search:
        search_clause = " AND p.title LIKE ?"
        params.append(f"%{search}%")

    query = f"""
    SELECT
        p.product_id_diy,
        p.title,
        p.price,
        p.price_per_unit,
        p.image_url,
        p.product_url,
        c.competitor_title,
        c.competitor_price_per_unit,
        c.competitor_url,
        c.competitor_image
    FROM products p
    LEFT JOIN competitor_prices c
    ON p.product_id_diy = c.product_id
    WHERE 1=1
    """

    if where_clause:
        query += " " + where_clause.replace("WHERE", "AND")

    query += search_clause

    query += """
    ORDER BY p.title
    """

    # params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()

    return rows