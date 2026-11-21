"""
src/data_loader.py
Data loading and caching layer for Pricing Comparison Analytics.
Connects to SQLite database (data/app.db) and provides cached dataframes for Streamlit.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

def get_db_path() -> str:
    """Returns absolute path to SQLite database."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "app.db")

def get_connection():
    """Initializes SQLite connection with foreign keys enabled."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}. Please run src/generate_data.py first.")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@st.cache_data(ttl=3600, show_spinner=False)
def load_pricing_view() -> pd.DataFrame:
    """
    Loads pre-joined 30-column analytical view v_pricing_analysis.
    Cached for 1 hour to guarantee sub-second dashboard rendering.
    """
    conn = get_connection()
    query = "SELECT * FROM v_pricing_analysis;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Cast dates and categorical types for performance
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"]).dt.date
    df["category_name"] = df["category_name"].astype("category")
    df["competitor_name"] = df["competitor_name"].astype("category")
    df["platform_type"] = df["platform_type"].astype("category")
    df["pci_tier"] = df["pci_tier"].astype("category")
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_price_history() -> pd.DataFrame:
    """
    Loads 30-day temporal price history joined with product and competitor dimensions.
    """
    conn = get_connection()
    query = """
    SELECT 
        ph.history_id,
        ph.product_id,
        p.sku_code,
        p.product_name,
        c.category_name,
        comp.competitor_name,
        comp.platform_type,
        ph.recorded_price,
        ph.effective_date
    FROM price_history ph
    JOIN products p ON ph.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    JOIN competitors comp ON ph.competitor_id = comp.competitor_id
    ORDER BY ph.effective_date ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["effective_date"] = pd.to_datetime(df["effective_date"]).dt.date
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_master_tables():
    """Returns raw master dimension dataframes for diagnostics."""
    conn = get_connection()
    categories = pd.read_sql_query("SELECT * FROM categories;", conn)
    competitors = pd.read_sql_query("SELECT * FROM competitors;", conn)
    products = pd.read_sql_query("SELECT * FROM products;", conn)
    snapshots = pd.read_sql_query("SELECT * FROM price_snapshots;", conn)
    conn.close()
    return {
        "categories": categories,
        "competitors": competitors,
        "products": products,
        "price_snapshots": snapshots
    }

def apply_global_filters(df: pd.DataFrame, selected_categories, selected_competitors) -> pd.DataFrame:
    """
    Applies shared sidebar filters to the analytical dataframe.
    """
    filtered = df.copy()
    if selected_categories:
        filtered = filtered[filtered["category_name"].isin(selected_categories)]
    if selected_competitors:
        filtered = filtered[filtered["competitor_name"].isin(selected_competitors)]
    return filtered
