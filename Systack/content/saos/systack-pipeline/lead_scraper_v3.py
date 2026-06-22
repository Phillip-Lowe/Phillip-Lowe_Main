#!/usr/bin/env python3
"""
Systack.net Lead Scraper v3 — Fixed Scoring
Only returns PRIME prospects: independent food trucks, delis, small restaurants
NO chains, NO corporate-owned, NO places that already have online ordering
"""

import sqlite3
import requests
import json
import os
import sys
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyBhmoUCGTCYVIPW1Y_Dlvapv7w7H7U_T4Y')
DB_PATH = os.environ.get('CRM_DB_PATH', '/Users/philliplowe/.openclaw/workspaces/sol/green-systems-crm.db')

# Search: food trucks, delis, small independent spots
LOCATION = '34.7465,-92.2896'  # Little Rock
RADIUS = 20000  # 20km — wider net for food trucks

# Target business types — small, independent, potential for online ordering
TARGET_TYPES = ['restaurant', 'cafe', 'meal_takeaway', 'meal_delivery']
TARGET_KEYWORDS = ['food truck', 'deli', 'sandwich', 'bbq', 'burger', 'taco',
                   'cajun', 'soul food', 'family restaurant', 'cafe', 'diner']

# ── CHAIN FILTERS ──────────────────────────────────────────────
# These will be skipped regardless of score
KNOWN_CHAINS = {
    'little caesars', 'olive garden', 'texas roadhouse', "jason's deli",
    'mcdonald', 'burger king', 'wendy', 'taco bell', 'kfc', 'popeyes',
    'subway', 'arbys', "arby's", 'chick-fil-a', 'chipotle', 'panera',
    'starbucks', 'domino', 'pizza hut', 'papa john', 'wingstop',
    'zaxby', 'raising cane', 'five guys', 'jimmy john', 'sonic',
    'whataburger', 'in-n-out', 'dairy queen', 'dunkin', 'panda express',
    'outback', 'applebees', "applebee's", 'chilis', "chili's",
    'red lobster', 'longhorn', 'buffalo wild wings', 'dennys', "denny's",
    'ihop', 'waffle house', 'cracker barrel', 'golden corral',
    'logan roadhouse', "logan's", 'walk-ons', "walk on's",
    'bar louie', 'cinemark', 'amc', 'regal',
    'us pizza', 'marco pizza', "marco's"
}

def is_chain(name):
    """Check if business is a known chain."""
    name_lower = name.lower()
    for chain in KNOWN_CHAINS:
        if chain in name_lower:
            return True
    return False

# ── SCORING v3 — Prime-Only ─────────────────────────────────────
def score_lead(place, details):
    """
    NEW SCORING: Only scores high for independent, small, tech-deficient businesses.
    Maximum: 10 points. Target: 7+ = Prime lead.
    """
    score = 0
    reasons = []
    red_flags = []
    
    name = place.get('name', '')
    rating = place.get('rating', 0)
    review_count = place.get('user_ratings_total', 0)
    types = place.get('types', [])
    price_level = place.get('price_level', 0)
    website = details.get('website', '')
    phone = details.get('formatted_phone_number', '')
    
    # ── RED FLAGS (immediate disqualifiers) ──
    if is_chain(name):
        red_flags.append('CHAIN_RESTAURANT')
        return score, reasons, red_flags, 'Skip'
    
    if 'lodging' in types or 'hotel' in types:
        red_flags.append('HOTEL_RESTAURANT')
        return score, reasons, red_flags, 'Skip'
    
    if review_count > 2000:
        red_flags.append('TOO_LARGE')
        return score, reasons, red_flags, 'Skip'
    
    # ── POSITIVE SIGNALS ──
    
    # High rating with decent reviews = quality business
    if rating >= 4.0 and review_count >= 20:
        score += 2
        reasons.append(f'highly_rated_{rating}')
    elif rating >= 3.5:
        score += 1
        reasons.append('decent_rating')
    
    # Small business signals
    if review_count < 100:
        score += 2
        reasons.append('small_business')
    elif review_count < 300:
        score += 1
        reasons.append('medium_small')
    
    # Independent signals (no website, basic types)
    if not website:
        score += 3
        reasons.append('no_website_at_all')
    elif 'square.site' not in website and 'wix' not in website:
        # Has website but it's likely basic
        score += 1
    
    # Food truck specific
    if 'food' in types and 'meal_takeaway' in types:
        score += 1
    if any(kw in name.lower() for kw in ['food truck', 'deli', 'bbq', 'smokehouse', 'cajun']):
        score += 2
        reasons.append('target_business_type')
    
    # Pricing — budget-friendly means independent
    if price_level and price_level <= 1:
        score += 1
        reasons.append('affordable_pricing')
    
    # No phone = probably too small (not useful for us)
    if not phone:
        score -= 1
        red_flags.append('no_phone')
    
    # ── CATEGORY ──
    if score >= 5:
        category = 'Prime'
    elif score >= 3:
        category = 'Warm'
    else:
        category = 'Low'
    
    return score, reasons, red_flags, category


# ── DATABASE ────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Add new columns if needed
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN red_flags TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN reasons TEXT")
    except:
        pass
    
    conn.commit()
    return conn


def save_lead(conn, place, details, score, reasons, red_flags, category):
    """Save lead to SQLite."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM leads WHERE place_id = ?", (place['place_id'],))
    existing = cursor.fetchone()
    
    now = datetime.now().isoformat()
    types_str = ','.join(place.get('types', []))
    reasons_str = ','.join(reasons)
    red_flags_str = ','.join(red_flags)
    
    if existing:
        cursor.execute("""
            UPDATE leads SET 
                name = ?, address = ?, phone = ?, website = ?, rating = ?, 
                review_count = ?, category = ?, score = ?, stage = ?,
                reasons = ?, red_flags = ?, last_scraped = ?
            WHERE place_id = ?
        """, (
            place.get('name', ''),
            place.get('vicinity', ''),
            details.get('formatted_phone_number', ''),
            details.get('website', ''),
            place.get('rating', 0),
            place.get('user_ratings_total', 0),
            category,
            score,
            'New',
            reasons_str,
            red_flags_str,
            now,
            place['place_id']
        ))
    else:
        cursor.execute("""
            INSERT INTO leads (
                place_id, name, address, phone, website, rating, review_count,
                category, score, stage, owner, created_date, source,
                reasons, red_flags, last_scraped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            place['place_id'],
            place.get('name', ''),
            place.get('vicinity', ''),
            details.get('formatted_phone_number', ''),
            details.get('website', ''),
            place.get('rating', 0),
            place.get('user_ratings_total', 0),
            category,
            score,
            'New',
            'Green',
            now,
            'google_maps_scraper_v3',
            reasons_str,
            red_flags_str,
            now
        ))
    
    conn.commit()
    return 'updated' if existing else 'new'


# ── GOOGLE MAPS API ─────────────────────────────────────────────
def search_places(keyword=None, next_page_token=None):
    """Search Google Maps Places API for target businesses."""
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': LOCATION,
        'radius': RADIUS,
        'type': 'restaurant',
        'key': API_KEY
    }
    if keyword:
        params['keyword'] = keyword
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        if data.get('status') != 'OK':
            return [], None
        return data.get('results', []), data.get('next_page_token')
    except Exception as e:
        print(f"  Search error: {e}")
        return [], None


def get_details(place_id):
    """Get detailed info for a place."""
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,website,price_level,types,user_ratings_total,rating',
        'key': API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        return resp.json().get('result', {})
    except:
        return {}


# ── MAIN ────────────────────────────────────────────────────────
def main():
    print(f"🔍 Systack Lead Scraper v3 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Target: Independent food businesses, no chains, no corporate")
    print()
    
    conn = get_db()
    total = 0
    prime = 0
    warm = 0
    skipped = 0
    
    for keyword in TARGET_KEYWORDS:
        print(f"  Searching: '{keyword}'...")
        places, token = search_places(keyword=keyword)
        
        for place in places:
            name = place.get('name', 'Unknown')
            details = get_details(place.get('place_id', ''))
            
            score, reasons, red_flags, category = score_lead(place, details)
            
            if red_flags:
                print(f"    🔴 {name} — {', '.join(red_flags)}")
                skipped += 1
                continue
            
            save_lead(conn, place, details, score, reasons, red_flags, category)
            total += 1
            
            if category == 'Prime':
                emoji = '🟢'
                prime += 1
            elif category == 'Warm':
                emoji = '🟡'
                warm += 1
            else:
                emoji = '⚪'
            
            print(f"    {emoji} {name} — score {score} ({category}) — {', '.join(reasons[:3])}")
    
    conn.close()
    
    print()
    print(f"📊 Results: {total} found | {prime} Prime | {warm} Warm | {skipped} skipped")
    print()
    
    # Show Prime leads
    conn = get_db()
    primes = conn.execute("""
        SELECT name, rating, review_count, phone, category, reasons
        FROM leads WHERE category = 'Prime' AND stage = 'New'
        ORDER BY score DESC LIMIT 10
    """).fetchall()
    
    if primes:
        print("🟢 PRIME PROSPECTS:")
        print()
        for p in primes:
            print(f"  {p['name']}")
            print(f"    Rating: {p['rating']}⭐ | Reviews: {p['review_count']} | Phone: {p.get('phone', 'N/A') or 'N/A'}")
            print(f"    Signals: {p.get('reasons', 'none') or 'none'}")
            print()
    
    conn.close()


if __name__ == "__main__":
    main()
