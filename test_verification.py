#!/usr/bin/env python3
"""
Test script to verify the eBay listing verification step
"""

import sqlite3
import os

def check_database():
    """Check the current state of listings in the database"""
    try:
        conn = sqlite3.connect('restyle_project/db.sqlite3')
        cursor = conn.cursor()
        
        # Check existing listings
        cursor.execute('''
            SELECT l.id, l.platform_item_id, l.is_active, i.title 
            FROM core_listing l 
            JOIN core_item i ON l.item_id = i.id 
            WHERE l.platform_item_id IS NOT NULL
        ''')
        listings = cursor.fetchall()
        
        print("=== Current Listings ===")
        for listing in listings:
            print(f"Listing ID: {listing[0]}, eBay ID: {listing[1]}, Active: {listing[2]}, Title: {listing[3]}")
        
        # Check items
        cursor.execute('SELECT id, title, brand FROM core_item LIMIT 5')
        items = cursor.fetchall()
        
        print("\n=== Available Items ===")
        for item in items:
            print(f"Item ID: {item[0]}, Title: {item[1]}, Brand: {item[2]}")
        
        conn.close()
        return listings, items
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return [], []

if __name__ == "__main__":
    print("Testing eBay listing verification...")
    listings, items = check_database()
    
    if listings:
        print(f"\nFound {len(listings)} existing listings with eBay IDs")
        print("You can test the verification by:")
        print("1. Creating a new listing through your app")
        print("2. Checking the logs for verification messages")
        print("3. Verifying the listing appears on eBay")
    else:
        print("No existing listings found. You can test by creating a new listing.") 