#!/usr/bin/env python3
"""Initialize Utopia Deli SQLite database with data from Google Sheets"""

import sqlite3
import os

DB_PATH = os.path.expanduser("~/.openclaw/workspaces/sol/data/utopia-deli.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Open hours
    cur.execute("""
        CREATE TABLE IF NOT EXISTS open_hours (
            day TEXT PRIMARY KEY,
            day_order INTEGER,
            open_time TEXT,
            close_time TEXT,
            is_open INTEGER
        )
    """)
    
    # Menu catalog
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_catalog (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            price_cents INTEGER,
            description TEXT,
            active INTEGER,
            image_url TEXT
        )
    """)
    
    # Orders log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            customer_name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            county TEXT,
            entree TEXT,
            modifiers TEXT,
            subtotal_cents INTEGER,
            tax_cents INTEGER,
            total_cents INTEGER,
            payment_link TEXT,
            status TEXT
        )
    """)
    
    # Insert open hours (from HTML: Mon-Sat 12:30 PM - 7:30 PM CT, Sun closed)
    hours = [
        ("Mon", 0, "12:30", "19:30", 1),
        ("Tue", 1, "12:30", "19:30", 1),
        ("Wed", 2, "12:30", "19:30", 1),
        ("Thu", 3, "12:30", "19:30", 1),
        ("Fri", 4, "12:30", "19:30", 1),
        ("Sat", 5, "12:30", "19:30", 1),
        ("Sun", 6, "00:00", "00:00", 0),
    ]
    cur.executemany("INSERT OR REPLACE INTO open_hours (day, day_order, open_time, close_time, is_open) VALUES (?, ?, ?, ?, ?)", hours)
    
    # Insert menu items (from web fetch of Google Sheet)
    menu_items = [
        ("COWBOY", "Cowboy Chik'n Sandwich", 1300, "Grilled Cowboy Chik'n, Lettuce, Tomato, Ranch, Bac'n.", 1, ""),
        ("CLUB", "Chik'n Club Sub", 1500, "Grilled Chik'n Bac'n Cheese on a bed of Lettuce and Tomatoes.", 1, ""),
        ("FRIED", "Chik'n Fried Chik'n Sub", 1300, "Crispy Fried Chik'n on a hoagie with lettuce, tomato, ranch.", 1, ""),
        ("PHILLY", "Philly Sub", 1300, "Stek OR Chik'n with sautéed onions & bell peppers", 1, ""),
        ("CHICKEN_PHILLY", "Chik'n Philly", 1300, "Chik'n with sautéed onions & bell peppers on a hoagie", 1, ""),
        ("POPPER", "Chik'n Poppers", 1000, "Crispy chikn dippers — choice of sauce", 1, ""),
    ]
    cur.executemany("INSERT OR REPLACE INTO menu_catalog (item_id, name, price_cents, description, active, image_url) VALUES (?, ?, ?, ?, ?, ?)", menu_items)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == '__main__':
    init_db()
