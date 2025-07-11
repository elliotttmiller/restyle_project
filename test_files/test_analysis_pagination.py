#!/usr/bin/env python3
"""
Test script to verify the analysis pagination functionality
"""

import requests
import json

def test_analysis_pagination():
    """Test the price analysis pagination functionality"""
    
    base_url = "http://localhost:8000"
    
    # Test data for a Jordan 4 search
    test_data = {
        "title": "Jordan Air Jordan 4 Retro Black Cat",
        "brand": "Jordan",
        "size": "10",
        "color": "Black",
        "condition": "NEW_WITH_TAGS"
    }
    
    print("🧪 Testing Price Analysis Pagination")
    print("=" * 50)
    
    try:
        # Test first page
        print("\n📄 Testing Page 1...")
        response1 = requests.post(f"{base_url}/api/core/price-analysis/", json=test_data)
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Page 1 successful")
            print(f"   - Comps found: {len(data1.get('comps', []))}")
            print(f"   - Has more: {data1.get('pagination', {}).get('has_more', False)}")
            print(f"   - Total items: {data1.get('pagination', {}).get('total_items', 0)}")
            
            # Test second page if available
            if data1.get('pagination', {}).get('has_more', False):
                print("\n📄 Testing Page 2...")
                test_data['page'] = 2
                response2 = requests.post(f"{base_url}/api/core/price-analysis/", json=test_data)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"✅ Page 2 successful")
                    print(f"   - Additional comps: {len(data2.get('comps', []))}")
                    print(f"   - Has more: {data2.get('pagination', {}).get('has_more', False)}")
                    
                    # Verify pagination info
                    pagination1 = data1.get('pagination', {})
                    pagination2 = data2.get('pagination', {})
                    
                    print(f"\n📊 Pagination Verification:")
                    print(f"   - Page 1: {pagination1.get('page')} of {pagination1.get('total_items')} items")
                    print(f"   - Page 2: {pagination2.get('page')} of {pagination2.get('total_items')} items")
                    print(f"   - Page size: {pagination1.get('page_size')}")
                    
                else:
                    print(f"❌ Page 2 failed: {response2.status_code}")
                    print(f"   Response: {response2.text}")
            else:
                print("ℹ️  No more pages available")
                
        else:
            print(f"❌ Page 1 failed: {response1.status_code}")
            print(f"   Response: {response1.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_analysis_pagination() 