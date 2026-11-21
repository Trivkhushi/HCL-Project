"""
src/cleaner.py
Data quality, anomaly detection, and data hygiene module for Pricing Comparison Analytics.
Detects missing values, duplicates, and extreme statistical price outliers using Z-scores.
"""

import pandas as pd
import numpy as np

def detect_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """
    Computes category-partitioned Z-scores for selling_price and flags extreme outliers (|Z| > threshold).
    """
    df_clean = df.copy()
    
    # Calculate group-level mean and std
    category_stats = df_clean.groupby("category_name", observed=True)["selling_price"].agg(["mean", "std"]).reset_index()
    category_stats.columns = ["category_name", "cat_mean", "cat_std"]
    
    df_merged = df_clean.merge(category_stats, on="category_name", how="left")
    
    # Avoid zero division
    df_merged["cat_std"] = df_merged["cat_std"].replace(0, np.nan)
    df_merged["z_score"] = (df_merged["selling_price"] - df_merged["cat_mean"]) / df_merged["cat_std"]
    df_merged["is_outlier"] = df_merged["z_score"].abs() > threshold
    
    return df_merged[df_merged["is_outlier"]].sort_values("z_score", ascending=False)

def get_data_quality_report(df: pd.DataFrame) -> dict:
    """
    Computes a comprehensive diagnostic report covering completeness, uniqueness, and validity.
    """
    total_rows = len(df)
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {col: round((count / total_rows) * 100.0, 2) for col, count in null_counts.items() if count > 0}
    
    # Duplicate SKU-Competitor checks
    duplicate_rows = df.duplicated(subset=["sku_code", "competitor_name"], keep=False).sum()
    
    # Outliers
    outliers_df = detect_outliers(df, threshold=3.0)
    
    # Memory footprint
    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    
    return {
        "total_records": total_rows,
        "total_columns": len(df.columns),
        "null_percentages": null_percentages,
        "duplicate_records": int(duplicate_rows),
        "outlier_count": len(outliers_df),
        "outliers_dataframe": outliers_df[["sku_code", "product_name", "category_name", "competitor_name", "selling_price", "mrp", "z_score"]],
        "memory_footprint_mb": memory_mb
    }
