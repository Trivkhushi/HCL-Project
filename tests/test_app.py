"""
tests/test_app.py
Technical tests (TC-T-12 to TC-T-14) verifying UI component importability,
database query execution latency (< 1.0 second), and memory footprint boundaries.
"""

import os
import time
import sqlite3
import pandas as pd
import pytest

def test_tc_t_12_ui_components_importable():
    """TC-T-12: Verify src.ui module loads and functions are callable."""
    from src.ui import render_tailwind_header, render_kpi_card, render_alert_box
    assert callable(render_tailwind_header)
    assert callable(render_kpi_card)
    assert callable(render_alert_box)

def test_tc_t_13_query_latency_under_one_second():
    """TC-T-13: Verify that querying v_pricing_analysis executes in under 1.0 second (latency SLA)."""
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
    assert os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    
    start_time = time.perf_counter()
    df = pd.read_sql("SELECT * FROM v_pricing_analysis;", conn)
    elapsed_time = time.perf_counter() - start_time
    
    conn.close()
    
    assert len(df) >= 300
    assert elapsed_time < 1.0, f"Query took {elapsed_time:.4f}s, exceeding 1.0s threshold"

def test_tc_t_14_memory_footprint_compact():
    """TC-T-14: Verify dataset in-memory memory footprint is well within limits (< 10 MB)."""
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM v_pricing_analysis;", conn)
    conn.close()
    
    mem_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    assert mem_usage_mb < 10.0, f"Memory usage is {mem_usage_mb:.2f} MB, exceeding 10 MB budget"
