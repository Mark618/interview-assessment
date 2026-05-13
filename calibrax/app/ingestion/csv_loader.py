import pandas as pd

from app.database.db import get_connection
from app.database.models import create_tables


def clean_data(df):

    # Remove junk columns
    df = df.drop(columns=["Column 1", "Unnamed: 76"], errors="ignore")

    # Remove rows missing critical prices
    # Or if missing given 
    df = df.dropna(subset=["s_price_diy", "s_price_competitor"])

    # Convert numeric columns
    numeric_columns = [
        "s_price_diy",
        "s_price_competitor",
        "s_price_per_unit_combined_diy",
        "s_price_per_unit_combined_competitor",
        "price_index",
        "normalised_price_index",
        "matching_score",
        "image_similarity"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows with invalid numeric conversions
    df = df.dropna(subset=["s_original_price_diy", "s_original_price_competitor"])

    df['s_original_price_diy'] = df['s_original_price_diy'].astype(float)
    df['s_original_price_competitor'] = df['s_original_price_competitor'].astype(float)


    df["cal_price_index"] = df["s_original_price_diy"] / df["s_original_price_competitor"]
    df['price_index'] = df['cal_price_index'].round(2)

    # Remove duplicate product-competitor pairs refer to this link https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html
    df = df.drop_duplicates(subset=["product_id_diy", "s_link_competitor"])

    return df


def insert_products(df, conn):

    products_df = df[[
        "product_id_diy",
        "s_title_diy",
        "s_brand_diy",
        "category",
        "segment",
        "collection",
        "product_type",
        "s_price_diy",
        "s_price_per_unit_combined_diy",
        "final_unit",
        "s_primary_image_diy",
        "s_link_diy"
    ]].drop_duplicates(subset=["product_id_diy"])

    products_df = products_df.rename(columns={
        "s_title_diy": "title",
        "s_brand_diy": "brand",
        "s_price_diy": "price",
        "s_price_per_unit_combined_diy": "price_per_unit",
        "s_primary_image_diy": "image_url",
        "s_link_diy": "product_url"
    })

    products_df.to_sql("products", conn, if_exists="append", index=False)


def insert_competitors(df, conn):

    competitors_df = df[[
        "product_id_diy",
        "s_vendor_competitor",
        "s_title_competitor",
        "s_price_competitor",
        "s_price_per_unit_combined_competitor",
        "matching_score",
        "image_similarity",
        "exact_match",
        "brand_match",
        "scent_match",
        "s_link_competitor",
        "s_primary_image_competitor"
    ]]

    competitors_df = competitors_df.rename(columns={
        "product_id_diy": "product_id",
        "s_vendor_competitor": "competitor_vendor",
        "s_title_competitor": "competitor_title",
        "s_price_competitor": "competitor_price",
        "s_price_per_unit_combined_competitor": "competitor_price_per_unit",
        "s_link_competitor": "competitor_url",
        "s_primary_image_competitor": "competitor_image"
    })
    competitors_df.to_sql("competitor_prices", conn, if_exists="append", index=False)


def load_csv_to_db(csv_path):

    print("Reading CSV...")

    df = pd.read_csv(csv_path)

    print("Cleaning data...")

    df = clean_data(df)

    conn = get_connection()

    print("Creating tables...")

    create_tables(conn)

    print("Inserting products...")

    insert_products(df, conn)

    print("Inserting competitor listings...")

    insert_competitors(df, conn)

    conn.close()

    print("Data ingestion completed.")