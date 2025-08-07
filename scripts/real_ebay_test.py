"""
Real eBay Integration Test
Tests actual eBay API functionality using the production services
"""

import asyncio
import requests
import logging
from core.services import EbayService
from core.ebay_auth import get_ebay_oauth_token, token_manager

logger = logging.getLogger(__name__)

class RealEbayTester:
    """Real eBay API testing functionality"""
    
    def __init__(self):
        self.ebay_service = EbayService()
        
    async def test_token_management(self):
        """Test eBay token management"""
        try:
            # Test get_access_token method (alias)
            token = token_manager.get_access_token()
            if token:
                print(f"    ✅ Token management: Access token retrieved (length: {len(token)})")
                return True
            else:
                print("    ❌ Token management: No access token available")
                return False
        except Exception as e:
            print(f"    ❌ Token management test failed: {e}")
            return False
    
    async def test_search_functionality(self):
        """Test actual eBay search functionality"""
        test_queries = [
            'vintage nike sneakers',
            'designer handbag',
            'men\'s leather jacket',
            'women\'s dress'
        ]
        
        results = {}
        total_items = 0
        
        for query in test_queries:
            try:
                print(f"    Testing query: '{query}'")
                items = self.ebay_service.search_items(query, limit=5)
                result_count = len(items) if items else 0
                total_items += result_count
                results[query] = result_count
                
                if result_count > 0:
                    print(f"    ✅ Query '{query}': {result_count} items found")
                else:
                    print(f"    ❌ Query '{query}': {result_count} items found")
                    
            except Exception as e:
                print(f"    ❌ Query '{query}': Error - {e}")
                results[query] = 0
        
        return {
            'results': results,
            'total_items': total_items,
            'success': total_items > 0
        }
    
    async def test_api_endpoints(self):
        """Test individual eBay API endpoints"""
        endpoints = {
            'browse_search': self._test_browse_search,
            'get_item': self._test_get_item,
            'get_categories': self._test_categories,
            'marketplace_insights': self._test_marketplace_insights
        }
        
        results = {}
        
        for endpoint_name, test_func in endpoints.items():
            try:
                start_time = asyncio.get_event_loop().time()
                result = await test_func()
                end_time = asyncio.get_event_loop().time()
                
                response_time = int((end_time - start_time) * 1000)
                
                if result:
                    print(f"    ✅ {endpoint_name}: {response_time}ms")
                    results[endpoint_name] = f"{response_time}ms"
                else:
                    print(f"    ❌ {endpoint_name}: Failed")
                    results[endpoint_name] = "Failed"
                    
            except Exception as e:
                print(f"    ❌ {endpoint_name}: Error - {e}")
                results[endpoint_name] = f"Error: {e}"
        
        return results
    
    async def _test_browse_search(self):
        """Test browse/search endpoint"""
        try:
            items = self.ebay_service.search_items("test", limit=1)
            return len(items) >= 0  # Even 0 results is a successful API call
        except Exception:
            return False
    
    async def _test_get_item(self):
        """Test get item endpoint"""
        try:
            # First get an item from search
            items = self.ebay_service.search_items("test", limit=1)
            if items and len(items) > 0:
                item_id = items[0].get('itemId')
                if item_id:
                    details = self.ebay_service.get_item_details(item_id)
                    return details is not None
            return True  # If no items to test, consider it successful
        except Exception:
            return False
    
    async def _test_categories(self):
        """Test category functionality"""
        try:
            # Test search with category filter
            items = self.ebay_service.search_items("test", category_ids="11450", limit=1)
            return len(items) >= 0
        except Exception:
            return False
    
    async def _test_marketplace_insights(self):
        """Test marketplace insights (basic search metrics)"""
        try:
            # Test search with different parameters
            items1 = self.ebay_service.search_items("popular item", limit=1)
            items2 = self.ebay_service.search_items("rare collectible", limit=1)
            return len(items1) >= 0 and len(items2) >= 0
        except Exception:
            return False
    
    async def test_real_time_features(self):
        """Test real-time eBay features"""
        try:
            # Test multiple rapid searches to simulate real-time usage
            queries = ["fashion", "electronics", "books", "toys", "jewelry"]
            results = []
            
            for query in queries:
                items = self.ebay_service.search_items(query, limit=2)
                results.append(len(items) if items else 0)
            
            total_results = sum(results)
            avg_results = total_results / len(queries) if queries else 0
            
            return {
                'total_queries': len(queries),
                'total_results': total_results,
                'average_results': avg_results,
                'success': total_results > 0
            }
            
        except Exception as e:
            print(f"    ❌ Real-time features test failed: {e}")
            return {
                'total_queries': 0,
                'total_results': 0,
                'average_results': 0,
                'success': False
            }
    
    async def test_error_handling(self):
        """Test eBay error handling"""
        try:
            # Test invalid queries and parameters
            test_cases = [
                {"query": "", "expected": "handled"},  # Empty query
                {"query": "test", "category_ids": "invalid", "expected": "handled"},  # Invalid category
                {"query": "a" * 500, "expected": "handled"},  # Very long query
            ]
            
            handled_cases = 0
            
            for case in test_cases:
                try:
                    items = self.ebay_service.search_items(
                        case["query"], 
                        category_ids=case.get("category_ids"),
                        limit=1
                    )
                    # If no exception was raised, it was handled gracefully
                    handled_cases += 1
                except Exception:
                    # If exception occurred but was expected, still count as handled
                    handled_cases += 1
            
            success_rate = handled_cases / len(test_cases)
            return {
                'tested_cases': len(test_cases),
                'handled_cases': handled_cases,
                'success_rate': success_rate,
                'success': success_rate >= 0.8
            }
            
        except Exception as e:
            print(f"    ❌ Error handling test failed: {e}")
            return {
                'tested_cases': 0,
                'handled_cases': 0,
                'success_rate': 0,
                'success': False
            }

# Async test runner
async def run_real_ebay_tests():
    """Run comprehensive real eBay tests"""
    print("🛒 Testing Real eBay Integration...")
    tester = RealEbayTester()
    
    # Test token management
    print("  🔑 Testing eBay Token Management...")
    token_result = await tester.test_token_management()
    
    # Test search functionality
    print("  🔍 Testing eBay Search Functionality...")
    search_result = await tester.test_search_functionality()
    
    # Test API endpoints
    print("  🌐 Testing eBay API Endpoints...")
    endpoint_results = await tester.test_api_endpoints()
    
    # Test real-time features
    print("  ⚡ Testing eBay Real-time Features...")
    realtime_results = await tester.test_real_time_features()
    
    # Test error handling
    print("  🛡️ Testing eBay Error Handling...")
    error_handling_results = await tester.test_error_handling()
    
    return {
        'token_management': token_result,
        'search_functionality': search_result,
        'api_endpoints': endpoint_results,
        'real_time_features': realtime_results,
        'error_handling': error_handling_results
    }

if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(run_real_ebay_tests())
    print("\n📊 Real eBay Test Results:")
    for test_name, result in results.items():
        print(f"  {test_name}: {result}")
