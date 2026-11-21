"""
tests/test_data.py
Technical tests (TC-T-01 to TC-T-05) verifying database connection, schema structure,
table row counts, unique primary keys, referential integrity, and analytical view definition.
"""

import os
import sqlite3
import pytest

@pytest.fixture(scope="module")
def db_connection():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
    assert os.path.exists(db_path), f"Database file does not exist at {db_path}"
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn
    conn.close()

def test_tc_t_01_database_exists(db_connection):
    """TC-T-01: Verify SQLite database connects and returns a valid cursor."""
    cursor = db_connection.cursor()
    cursor.execute("SELECT sqlite_version();")
    version = cursor.fetchone()
    assert version is not None
    assert len(version[0]) > 0

def test_tc_t_02_table_row_counts(db_connection):
    """TC-T-02: Verify planned row counts across all master dimensions and fact tables."""
    cursor = db_connection.cursor()
    
    counts = {}
    tables = ["categories", "competitors", "products", "price_snapshots", "price_history"]
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        counts[t] = cursor.fetchone()[0]
        
    assert counts["categories"] == 4, f"Expected 4 categories, got {counts['categories']}"
    assert counts["competitors"] == 6, f"Expected 6 competitors, got {counts['competitors']}"
    assert counts["products"] == 300, f"Expected 300 products, got {counts['products']}"
    assert counts["price_snapshots"] >= 300, f"Expected >= 300 snapshots, got {counts['price_snapshots']}"
    assert counts["price_history"] >= 1800, f"Expected >= 1800 history records, got {counts['price_history']}"

def test_tc_t_03_primary_key_uniqueness(db_connection):
    """TC-T-03: Verify primary key uniqueness across all tables (0 duplicate PKs)."""
    cursor = db_connection.cursor()
    
    pk_map = {
        "categories": "category_id",
        "competitors": "competitor_id",
        "products": "product_id",
        "price_snapshots": "snapshot_id",
        "price_history": "history_id"
    }
    
    for table, pk in pk_map.items():
        cursor.execute(f"""
            SELECT {pk}, COUNT(*) 
            FROM {table} 
            GROUP BY {pk} 
            HAVING COUNT(*) > 1;
        """)
        dupes = cursor.fetchall()
        assert len(dupes) == 0, f"Found duplicate primary keys in {table}: {dupes}"

def test_tc_t_04_foreign_key_integrity(db_connection):
    """TC-T-04: Verify referential integrity with zero orphaned foreign keys."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_key_check;")
    violations = cursor.fetchall()
    assert len(violations) == 0, f"Foreign key check failed with violations: {violations}"

def test_tc_t_05_analytical_view_columns(db_connection):
    """TC-T-05: Verify v_pricing_analysis view exists and provides required columns."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(v_pricing_analysis);")
    columns = [row[1] for row in cursor.fetchall()]
    assert len(columns) >= 30, f"Expected >= 30 columns in view, got {len(columns)}"
    
    required_cols = [
        "snapshot_id", "product_id", "sku_code", "category_name", "cost_price",
        "mrp", "competitor_name", "platform_type", "selling_price", "discount_pct",
        "effective_cart_price", "gross_margin_pct", "is_margin_bleed", "price_competitiveness_index",
        "pci_tier", "market_avg_price"
    ]
    for col in required_cols:
        assert col in columns, f"Missing required column '{col}' in analytical view v_pricing_analysis"
