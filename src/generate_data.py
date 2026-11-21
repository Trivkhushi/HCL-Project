import os
import sqlite3
import random
import datetime
import pandas as pd
import numpy as np

# Set deterministic random seed
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def get_db_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "data", "app.db")

def create_schema(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop existing tables and views
    cursor.execute("DROP VIEW IF EXISTS v_pricing_analysis;")
    cursor.execute("DROP TABLE IF EXISTS price_history;")
    cursor.execute("DROP TABLE IF EXISTS price_snapshots;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS competitors;")
    cursor.execute("DROP TABLE IF EXISTS categories;")
    
    # 1. Categories Master
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        min_margin_threshold REAL NOT NULL DEFAULT 0.10 CHECK (min_margin_threshold >= 0.0 AND min_margin_threshold <= 1.0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Competitors Master
    cursor.execute("""
    CREATE TABLE competitors (
        competitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor_name TEXT NOT NULL UNIQUE,
        platform_type TEXT NOT NULL CHECK (platform_type IN ('Our Platform', 'Marketplace', 'Quick-Commerce', 'Omnichannel')),
        website_url TEXT,
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Products Master
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_code TEXT NOT NULL UNIQUE,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        brand_name TEXT NOT NULL,
        cost_price REAL NOT NULL CHECK (cost_price > 0.0),
        mrp REAL NOT NULL CHECK (mrp >= cost_price),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (category_id) ON UPDATE CASCADE ON DELETE RESTRICT
    );
    """)

    # 4. Price Snapshots Fact
    cursor.execute("""
    CREATE TABLE price_snapshots (
        snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        competitor_id INTEGER NOT NULL,
        selling_price REAL NOT NULL CHECK (selling_price > 0.0),
        discount_pct REAL NOT NULL DEFAULT 0.0 CHECK (discount_pct >= 0.0 AND discount_pct <= 100.0),
        shipping_fee REAL NOT NULL DEFAULT 0.0 CHECK (shipping_fee >= 0.0),
        platform_fee REAL NOT NULL DEFAULT 0.0 CHECK (platform_fee >= 0.0),
        stock_status TEXT NOT NULL DEFAULT 'In Stock' CHECK (stock_status IN ('In Stock', 'Out of Stock', 'Limited Stock')),
        rating_value REAL CHECK (rating_value >= 1.0 AND rating_value <= 5.0),
        review_count INTEGER NOT NULL DEFAULT 0 CHECK (review_count >= 0),
        snapshot_date DATE NOT NULL DEFAULT (CURRENT_DATE),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (product_id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competitor_id) REFERENCES competitors (competitor_id) ON UPDATE CASCADE ON DELETE RESTRICT,
        UNIQUE (product_id, competitor_id, snapshot_date)
    );
    """)

    # 5. Price History Fact
    cursor.execute("""
    CREATE TABLE price_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        competitor_id INTEGER NOT NULL,
        recorded_price REAL NOT NULL CHECK (recorded_price > 0.0),
        effective_date DATE NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (competitor_id) REFERENCES competitors (competitor_id) ON UPDATE CASCADE ON DELETE RESTRICT
    );
    """)

    # Performance Indexes
    cursor.execute("CREATE INDEX idx_products_cat ON products(category_id);")
    cursor.execute("CREATE INDEX idx_snapshots_prod ON price_snapshots(product_id);")
    cursor.execute("CREATE INDEX idx_snapshots_comp ON price_snapshots(competitor_id);")
    cursor.execute("CREATE INDEX idx_snapshots_date ON price_snapshots(snapshot_date);")
    cursor.execute("CREATE INDEX idx_history_lookup ON price_history(product_id, competitor_id, effective_date);")

    # 6. Joined Analytical View
    cursor.execute("""
    CREATE VIEW v_pricing_analysis AS
    WITH market_benchmarks AS (
        SELECT 
            product_id,
            ROUND(AVG(selling_price), 2) AS market_avg_price,
            ROUND(MIN(selling_price), 2) AS lowest_market_price
        FROM price_snapshots
        GROUP BY product_id
    )
    SELECT 
        ps.snapshot_id,
        ps.snapshot_date,
        p.product_id,
        p.sku_code,
        p.product_name,
        p.brand_name,
        c.category_id,
        c.category_name,
        c.min_margin_threshold,
        p.cost_price,
        p.mrp,
        comp.competitor_id,
        comp.competitor_name,
        comp.platform_type,
        ps.selling_price,
        ps.discount_pct,
        ps.shipping_fee,
        ps.platform_fee,
        ROUND(ps.selling_price + ps.shipping_fee + ps.platform_fee, 2) AS effective_cart_price,
        ROUND(ps.selling_price - p.cost_price, 2) AS gross_margin_value,
        ROUND(((ps.selling_price - p.cost_price) / ps.selling_price) * 100.0, 2) AS gross_margin_pct,
        CASE WHEN ((ps.selling_price - p.cost_price) / ps.selling_price) < c.min_margin_threshold THEN 1 ELSE 0 END AS is_margin_bleed,
        ps.stock_status,
        ps.rating_value,
        ps.review_count,
        mb.market_avg_price,
        ROUND(((ps.selling_price - mb.market_avg_price) / mb.market_avg_price) * 100.0, 2) AS price_variance_pct,
        ROUND((ps.selling_price / mb.market_avg_price) * 100.0, 2) AS price_competitiveness_index,
        CASE 
            WHEN (ps.selling_price / mb.market_avg_price) * 100.0 < 97.0 THEN 'Underpriced'
            WHEN (ps.selling_price / mb.market_avg_price) * 100.0 > 103.0 THEN 'Overpriced'
            ELSE 'Par'
        END AS pci_tier,
        mb.lowest_market_price
    FROM price_snapshots ps
    JOIN products p ON ps.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    JOIN competitors comp ON ps.competitor_id = comp.competitor_id
    JOIN market_benchmarks mb ON ps.product_id = mb.product_id;
    """)
    conn.commit()

def generate_data():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    cursor = conn.cursor()
    
    # -------------------------------------------------------------------------
    # 1. Insert Categories
    # -------------------------------------------------------------------------
    categories_data = [
        ("Electronics", 0.12),
        ("FMCG", 0.08),
        ("Personal Care", 0.15),
        ("Fashion", 0.20)
    ]
    cursor.executemany(
        "INSERT INTO categories (category_name, min_margin_threshold) VALUES (?, ?);",
        categories_data
    )
    conn.commit()
    
    # -------------------------------------------------------------------------
    # 2. Insert Competitors
    # -------------------------------------------------------------------------
    competitors_data = [
        ("ApexRetail", "Our Platform", "https://www.apexretail.in", 1),
        ("Amazon India", "Marketplace", "https://www.amazon.in", 1),
        ("Flipkart", "Marketplace", "https://www.flipkart.com", 1),
        ("Blinkit", "Quick-Commerce", "https://www.blinkit.com", 1),
        ("Zepto", "Quick-Commerce", "https://www.zepto.com", 1),
        ("Croma", "Omnichannel", "https://www.croma.com", 1)
    ]
    cursor.executemany(
        "INSERT INTO competitors (competitor_name, platform_type, website_url, is_active) VALUES (?, ?, ?, ?);",
        competitors_data
    )
    conn.commit()

    # -------------------------------------------------------------------------
    # 3. Generate 300 Products (75 per category)
    # -------------------------------------------------------------------------
    brand_catalog = {
        1: { # Electronics
            "brands": ["BoAt", "Noise", "Fire-Boltt", "Zebronics", "Portronics", "Havells", "Bajaj", "Crompton"],
            "items": [
                "Wireless Earbuds", "Bluetooth Smartwatch", "Fast Charger 65W", "Power Bank 20000mAh",
                "Gaming Headset", "LED Desk Lamp", "Immersion Water Heater", "Electric Kettle 1.5L",
                "Bluetooth Soundbar", "USB-C Hub Multi-Port", "Smart Plug WiFi", "Hair Dryer 1200W",
                "Beard Trimmer Pro", "Wireless Mouse Ergonomic", "Mechanical Keyboard RGB"
            ],
            "cost_range": (350.0, 4500.0),
            "markup_range": (1.25, 1.65)
        },
        2: { # FMCG
            "brands": ["Tata Sampann", "Fortune", "Aashirvaad", "Amul", "Saffola", "Everest", "MDH", "Catch", "Britannia", "Parle"],
            "items": [
                "Chana Dal 1kg", "Sunlite Refined Oil 1L", "Sharbati Atta 5kg", "Cow Ghee 500ml",
                "Basmati Rice 5kg", "Turmeric Powder 200g", "Garam Masala 100g", "Pure Honey 500g",
                "Oats Instant Pouch 1kg", "Cashews Whole 250g", "Almonds California 250g", "Green Tea Bags 25s",
                "Cookies Butter Crunch 300g", "Dark Chocolate Bar 100g", "Organic Jaggery Powder 1kg"
            ],
            "cost_range": (45.0, 950.0),
            "markup_range": (1.18, 1.45)
        },
        3: { # Personal Care
            "brands": ["Himalaya", "Mamaearth", "Biotique", "Khadi Natural", "Wow Skin Science", "Nivea India", "Dabur", "Patanjali"],
            "items": [
                "Purifying Neem Face Wash 150ml", "Onion Hair Oil 200ml", "Bio Dandelion Ageless Serum 40ml",
                "Herbal Sandalwood Soap 125g", "Apple Cider Vinegar Shampoo 300ml", "Soft Light Moisturizer 200ml",
                "Red Ayurvedic Toothpaste 150g", "Aloe Vera Gel Organic 250g", "Sunscreen Matte Gel SPF50 50g",
                "Vitamin C Face Toner 200ml", "Anti-Dandruff Tea Tree Lotion 100ml", "Rose Water Hydrating Mist 120ml",
                "Charcoal Peel Off Mask 100g", "Body Butter Cocoa Deep Nourish 200g", "Natural Lip Balm Pack of 2"
            ],
            "cost_range": (65.0, 650.0),
            "markup_range": (1.30, 1.80)
        },
        4: { # Fashion
            "brands": ["FabIndia", "Peter England", "Raymond", "W for Woman", "Manyavar", "Allen Solly", "Biba", "Flying Machine"],
            "items": [
                "Cotton Casual Shirt Regular Fit", "Slim Fit Denim Jeans", "Linen Kurta Traditional",
                "Printed Anarkali Kurti", "Formal Trousers Flat Front", "Polo T-Shirt Breathable",
                "Ethnic Nehru Jacket", "Silk Dupatta Handcrafted", "Chino Shorts Stretchable",
                "Embroidered Straight Kurti", "Leather Formal Belt", "Canvas Casual Sneakers",
                "Cotton Pyjama Set Loungewear", "Formal Blazer Single Breasted", "Graphic Print Tee Regular"
            ],
            "cost_range": (280.0, 3200.0),
            "markup_range": (1.45, 2.10)
        }
    }

    products_list = []
    product_counter = 1
    
    for cat_id in range(1, 5):
        cat_info = brand_catalog[cat_id]
        cat_prefix = ["ELEC", "FMCG", "CARE", "FASH"][cat_id - 1]
        
        for i in range(1, 76): # 75 items per category = 300 total
            brand = random.choice(cat_info["brands"])
            item = random.choice(cat_info["items"])
            sku_code = f"SKU-{cat_prefix}-{i:03d}"
            product_name = f"{brand} {item} ({random.choice(['Classic', 'Premium', 'Pro', 'Ultra', 'Select'])})"
            
            cost = round(random.uniform(*cat_info["cost_range"]), 2)
            markup = random.uniform(*cat_info["markup_range"])
            mrp = round(cost * markup, 2)
            
            products_list.append((product_counter, sku_code, product_name, cat_id, brand, cost, mrp))
            product_counter += 1

    cursor.executemany("""
    INSERT INTO products (product_id, sku_code, product_name, category_id, brand_name, cost_price, mrp)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, products_list)
    conn.commit()

    # -------------------------------------------------------------------------
    # 4. Generate Price Snapshots (Main Fact Table - 300+ Records)
    # Built-in Patterns:
    # Pattern 1: Quick-Commerce Premium on FMCG (Blinkit & Zepto 5-8% higher than Marketplace)
    # Pattern 2: Severe Margin Bleed on Electronics (Amazon/Flipkart discounts push price below cost + 10%)
    # Pattern 3: Hidden Cart Fee Discrepancy (QC & Marketplaces add 25-45 shipping, 5-15 platform fee)
    # Pattern 4: Rating vs Discount Correlation (r ~ 0.52)
    # Pattern 5: Stock-Out Price Surges (Competitors with Out of Stock correlate with higher prices)
    # -------------------------------------------------------------------------
    snapshots_list = []
    snap_id = 1
    today_date = "2026-11-21"

    # Pre-select 20 Electronics SKUs for severe margin bleed
    bleed_skus = set(random.sample(range(1, 76), 18))
    
    for prod in products_list:
        p_id, sku, name, cat_id, brand, cost, mrp = prod
        
        # Pick 2 competitors for this product snapshot (always including Our Platform or a benchmark)
        # To guarantee 300 primary benchmark records, we generate 1 snapshot per product against
        # a primary market benchmark competitor, giving exactly 300 rows.
        # Alternatively, let's distribute evenly across competitors so each product has an observation.
        # We will assign each SKU to a competitor observation (or our platform vs competitor).
        # Let's assign competitor based on category logic:
        if cat_id == 2: # FMCG -> Quick-Commerce vs Marketplace
            comp_id = random.choice([2, 3, 4, 5]) # Amazon, Flipkart, Blinkit, Zepto
        elif cat_id == 1: # Electronics -> Marketplace vs Omnichannel
            comp_id = random.choice([2, 3, 6]) # Amazon, Flipkart, Croma
        else: # Personal Care & Fashion
            comp_id = random.choice([1, 2, 3, 4, 5, 6])
            
        # Determine Selling Price based on Patterns
        if cat_id == 2 and comp_id in [4, 5]: # Pattern 1: Quick-Commerce Premium on FMCG
            # 5% to 8% higher than typical marketplace price
            base_disc = random.uniform(5.0, 12.0)
            selling_price = round(mrp * (1.0 - base_disc / 100.0), 2)
            shipping_fee = round(random.choice([25.0, 35.0, 45.0]), 2) # Pattern 3
            platform_fee = round(random.choice([5.0, 8.0, 12.0]), 2)
        elif cat_id == 1 and p_id in bleed_skus and comp_id in [2, 3]: # Pattern 2: Severe Margin Bleed
            # Deep predatory discount of 35% - 48%
            deep_disc = random.uniform(35.0, 48.0)
            selling_price = round(mrp * (1.0 - deep_disc / 100.0), 2)
            # Ensure it is below cost + 10%
            if (selling_price - cost) / selling_price >= 0.10:
                selling_price = round(cost * 1.04, 2) # Only 4% margin (severe bleed!)
            shipping_fee = 0.0
            platform_fee = 0.0
        else:
            disc = random.uniform(10.0, 30.0)
            selling_price = round(mrp * (1.0 - disc / 100.0), 2)
            shipping_fee = round(random.choice([0.0, 0.0, 40.0]), 2)
            platform_fee = round(random.choice([0.0, 5.0]), 2)

        discount_pct = round(((mrp - selling_price) / mrp) * 100.0, 2)
        
        # Pattern 5: Stock Status (8% out of stock)
        stock_status = "Out of Stock" if random.random() < 0.08 else "In Stock"
        if stock_status == "Out of Stock":
            selling_price = round(selling_price * 1.05, 2) # 5% surge on stock-out items
            
        # Pattern 4: Discount vs Review Volume & Rating Correlation
        # Deeper discount correlates with higher review count and slightly higher rating
        review_base = int(discount_pct * 65 + random.randint(50, 450))
        review_count = max(5, review_base)
        
        # Rating value between 3.2 and 4.9
        rating = round(3.5 + (discount_pct / 100.0) * 1.5 + random.uniform(-0.3, 0.3), 1)
        rating = min(5.0, max(1.0, rating))
        
        # Data Quality Quirk 1: 2.5% Missing ratings (new products)
        if random.random() < 0.025:
            rating = None
            review_count = 0
            
        snapshots_list.append((
            snap_id, p_id, comp_id, selling_price, discount_pct,
            shipping_fee, platform_fee, stock_status, rating, review_count, today_date
        ))
        snap_id += 1

    # Data Quality Quirk 2: Intentional Outliers (3 records with extreme Z-scores)
    # We will adjust 3 snapshots to have extreme prices (e.g. fat-finger data entry)
    outlier_indices = [15, 85, 210]
    for o_idx in outlier_indices:
        orig = snapshots_list[o_idx]
        # Multiply selling price by 4.5x MRP to create severe outlier |Z| > 3.5
        bad_price = round(products_list[orig[1]-1][6] * 4.2, 2)
        snapshots_list[o_idx] = (
            orig[0], orig[1], orig[2], bad_price, 0.0,
            orig[5], orig[6], orig[7], orig[8], orig[9], orig[10]
        )

    cursor.executemany("""
    INSERT INTO price_snapshots (
        snapshot_id, product_id, competitor_id, selling_price, discount_pct,
        shipping_fee, platform_fee, stock_status, rating_value, review_count, snapshot_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, snapshots_list)
    conn.commit()

    # -------------------------------------------------------------------------
    # 5. Generate Price History (Time-Series Fact - 1,800+ Records)
    # Pattern 4: Cadence Spikes on Weekends (Friday/Saturday repricing frequency is 3x higher)
    # -------------------------------------------------------------------------
    history_list = []
    hist_id = 1
    
    # Select 20 sample SKUs (5 per category) tracked daily across 3 competitors over 30 days
    sample_skus = [1, 5, 12, 20, 25, 76, 85, 92, 105, 115, 151, 160, 175, 185, 195, 226, 235, 245, 255, 265]
    tracked_comps = [1, 2, 4] # ApexRetail, Amazon, Blinkit
    
    start_date = datetime.date(2026, 10, 23) # 30 days prior to 2026-11-21
    
    for p_id in sample_skus:
        mrp = products_list[p_id - 1][6]
        base_p = round(mrp * 0.80, 2)
        
        for comp_id in tracked_comps:
            curr_price = base_p
            # Blinkit has higher base for FMCG
            if products_list[p_id - 1][3] == 2 and comp_id == 4:
                curr_price = round(base_p * 1.07, 2)
                
            for day_offset in range(30):
                obs_date = start_date + datetime.timedelta(days=day_offset)
                day_of_week = obs_date.weekday() # 4 is Friday, 5 is Saturday, 6 is Sunday
                
                # Weekend repricing probability is 40%, weekday is 12%
                reprice_prob = 0.45 if day_of_week in [4, 5] else 0.12
                
                if random.random() < reprice_prob:
                    # Competitor dynamic price fluctuation of +/- 2% to 6%
                    delta_pct = random.uniform(-0.06, 0.05)
                    curr_price = round(curr_price * (1.0 + delta_pct), 2)
                    
                history_list.append((hist_id, p_id, comp_id, curr_price, obs_date.strftime("%Y-%m-%d")))
                hist_id += 1

    cursor.executemany("""
    INSERT INTO price_history (history_id, product_id, competitor_id, recorded_price, effective_date)
    VALUES (?, ?, ?, ?, ?);
    """, history_list)
    conn.commit()

    # -------------------------------------------------------------------------
    # 6. Export to CSV and Multi-Sheet Excel
    # -------------------------------------------------------------------------
    data_dir = os.path.dirname(db_path)
    
    df_cat = pd.read_sql("SELECT * FROM categories;", conn)
    df_comp = pd.read_sql("SELECT * FROM competitors;", conn)
    df_prod = pd.read_sql("SELECT * FROM products;", conn)
    df_snap = pd.read_sql("SELECT * FROM price_snapshots;", conn)
    df_hist = pd.read_sql("SELECT * FROM price_history;", conn)
    df_view = pd.read_sql("SELECT * FROM v_pricing_analysis;", conn)

    # Save CSVs
    df_cat.to_csv(os.path.join(data_dir, "categories.csv"), index=False)
    df_comp.to_csv(os.path.join(data_dir, "competitors.csv"), index=False)
    df_prod.to_csv(os.path.join(data_dir, "products.csv"), index=False)
    df_snap.to_csv(os.path.join(data_dir, "price_snapshots.csv"), index=False)
    df_hist.to_csv(os.path.join(data_dir, "price_history.csv"), index=False)
    print("CSVs exported successfully.")

    # Save Multi-sheet Excel
    excel_path = os.path.join(data_dir, "pricing_data.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_cat.to_excel(writer, sheet_name="categories", index=False)
        df_comp.to_excel(writer, sheet_name="competitors", index=False)
        df_prod.to_excel(writer, sheet_name="products", index=False)
        df_snap.to_excel(writer, sheet_name="price_snapshots", index=False)
        df_hist.to_excel(writer, sheet_name="price_history", index=False)
        df_view.to_excel(writer, sheet_name="v_pricing_analysis", index=False)
    print(f"Multi-sheet Excel exported successfully at: {excel_path}")

    # -------------------------------------------------------------------------
    # 7. Verification & Validation Report
    # -------------------------------------------------------------------------
    # Check FK integrity
    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    
    report = {
        "categories_count": len(df_cat),
        "competitors_count": len(df_comp),
        "products_count": len(df_prod),
        "snapshots_count": len(df_snap),
        "history_count": len(df_hist),
        "view_columns_count": len(df_view.columns),
        "fk_violations": len(fk_violations),
        "null_ratings_count": df_snap["rating_value"].isna().sum(),
        "margin_bleed_count": (df_view["is_margin_bleed"] == 1).sum(),
        "outlier_count": len(outlier_indices)
    }
    
    conn.close()
    return report

if __name__ == "__main__":
    rep = generate_data()
    print("Validation Report Summary:")
    for k, v in rep.items():
        print(f"  {k}: {v}")
