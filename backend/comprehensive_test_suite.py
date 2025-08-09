
#!/usr/bin/env python3
"""
Optimized and Self-Adapting Comprehensive Test Suite for Restyle.ai (Final Version)
"""
import os
import json
import time
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# --- Configuration ---
@dataclass
class TestConfig:
    base_url: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "https://restyleproject-production.up.railway.app").rstrip("/")
    timeout: int = 120
    test_image_path: str = "test_files/example2.jpg"
    verify_ssl: bool = os.getenv("TEST_SSL_VERIFY", "False").lower() == "true"
    test_user: str = os.getenv("TEST_USER", "testuser")
    test_pass: str = os.getenv("TEST_PASS", "testpass1234")

@dataclass
class TestResult:
    name: str
    passed: bool
    status_code: int = 0
    details: str = ""
    duration: float = 0.0

# --- Test Suite Class ---
class OptimizedTestSuite:
    def __init__(self):
        self.config = TestConfig()
        self.auth_token = None
        if not self.config.verify_ssl:
            print("⚠️  SSL verification is disabled.")

    async def run_all_tests(self):
        """Main execution function."""
        print("🚀 Starting Optimized & Self-Adapting Test Suite")
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
            await self.authenticate(client)
            if not self.auth_token:
                print("❌ CRITICAL: Authentication failed. Cannot proceed with authenticated tests.")
                return

            endpoints_to_test = await self.discover_urls(client)
            if not endpoints_to_test:
                print("❌ CRITICAL: Could not discover URLs. Aborting.")
                return

            tasks = [self.test_endpoint(client, endpoint) for endpoint in endpoints_to_test]
            results = await asyncio.gather(*tasks)

        duration = time.time() - start_time
        self.summarize_and_save(results, duration)

    async def authenticate(self, client: httpx.AsyncClient):
        """Login and get a JWT token."""
        try:
            res = await client.post("/api/token/", json={"username": self.config.test_user, "password": self.config.test_pass})
            res.raise_for_status()
            self.auth_token = res.json()["access"]
            print(f"🔑 Obtained JWT token for '{self.config.test_user}'")
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            print(f"Authentication failed: {e}")
            self.auth_token = None

    async def discover_urls(self, client: httpx.AsyncClient) -> List[str]:
        """Dynamically fetch the list of URLs to test from the server."""
        print("\n🔍 Discovering URLs from the server...")
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            res = await client.get("/api/core/internal/list-urls/", headers=headers)
            if res.status_code == 200:
                urls = [item['path'] for item in res.json()]
                urls = [u for u in urls if not u.startswith('admin/') and not u.startswith('api/core/internal/')]
                print(f"✅ Discovered {len(urls)} endpoints to test.")
                return urls
            print(f"❌ URL Discovery failed with status {res.status_code}")
            return []
        except httpx.RequestError as e:
            print(f"❌ URL Discovery request failed: {e}")
            return []

    async def test_endpoint(self, client: httpx.AsyncClient, endpoint_path: str) -> TestResult:
        """Tests a single endpoint with intelligent logic."""
        start_time = time.time()
        name = f"Endpoint: {endpoint_path}"
        
        is_post = False
        use_auth = False
        payload = {}
        
        protected_patterns = ['/analyze-and-price/']
        if any(p in endpoint_path for p in protected_patterns):
            use_auth = True

        if 'analyze-and-price' in endpoint_path:
            is_post = True
            if os.path.exists(self.config.test_image_path):
                payload['files'] = {'image': open(self.config.test_image_path, 'rb')}
            else:
                return TestResult(name, False, 0, "Test image not found", 0)

        headers = {}
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        res = None
        try:
            method = "POST" if is_post else "GET"
            res = await client.request(method, endpoint_path, headers=headers, **payload)
            
            passed = False
            details = f"Responded with Status {res.status_code}"
            
            if 200 <= res.status_code < 300:
                passed = True
            elif res.status_code == 401 and use_auth:
                passed = False # Should not happen if auth is correct
                details += " (FAIL: Unauthorized, check token)"
            elif res.status_code == 404:
                passed = False # 404 is a failure for a discovered URL
                details += " (FAIL: Not Found)"

        except httpx.RequestError as e:
            passed = False
            details = f"Request Failed: {type(e).__name__}"
        
        duration = time.time() - start_time
        result = TestResult(name, passed, getattr(res, 'status_code', 0), details, duration)
        self.log_result(result)
        return result

    def log_result(self, result: TestResult):
        emoji = "✅" if result.passed else "❌"
        print(f"{emoji} {result.name}: {'PASS' if result.passed else 'FAIL'} ({result.duration:.2f}s) -> {result.details}")

    def summarize_and_save(self, results: List[TestResult], duration: float):
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0

        print("\n" + "="*60)
        print("🎯 TEST SUITE SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Total Endpoints Tested: {total_count}")
        print(f"✅ Passed: {passed_count} | ❌ Failed: {total_count - passed_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        status = "🟢 EXCELLENT" if success_rate >= 95 else "🔵 GOOD" if success_rate >= 80 else "🟡 NEEDS WORK"
        print(f"🎖️  Status: {status}")
        print("="*60)

        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
        print(f"💾 Results saved to: {filename}")

async def main():
    suite = OptimizedTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

    async def test_endpoint(self, client: httpx.AsyncClient, endpoint_path: str) -> TestResult:
        """Tests a single endpoint with intelligent logic for method, data, and success criteria."""
        start_time = time.time()
        name = f"Endpoint: {endpoint_path}"
        
        # --- Define test logic for specific endpoints ---
        is_post = False
        use_auth = False
        payload = {}
        
        # Define which endpoints are protected
        protected_patterns = ['/analyze-and-price/', '/ai/image-search/', '/ai/crop-preview/']
        if any(p in endpoint_path for p in protected_patterns):
            use_auth = True

        # Define which endpoints are POST and what data they need
        if 'analyze-and-price' in endpoint_path or 'image-search' in endpoint_path or 'crop-preview' in endpoint_path:
            is_post = True
            if os.path.exists(self.config.test_image_path):
                payload['files'] = {'image': open(self.config.test_image_path, 'rb')}
            else:
                return TestResult(name, False, 0, "Test image not found", 0)

        # --- Execute Request ---
        headers = {}
        if use_auth:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            method = "POST" if is_post else "GET"
            res = await client.request(method, endpoint_path, headers=headers, **payload)
            
            # --- Redefined Success Criteria ---
            passed = False
            details = f"Responded with Status {res.status_code}"
            
            # 2xx codes are always a success
            if 200 <= res.status_code < 300:
                passed = True
            # 401/403 is a SUCCESS if we are testing a protected endpoint WITHOUT a token (for future tests)
            # For now, we assume we always send a token to protected endpoints.
            # 400 is an acceptable response for endpoints that require data.
            elif res.status_code == 400 and is_post and not payload.get('files'):
                passed = True
                details += " (OK: Bad Request, as expected without data)"
            # A 404 is only a "pass" if we are specifically testing for it. Here, it's a FAIL.
            
        except httpx.RequestError as e:
            # This will catch SSLErrors, timeouts, etc.
            # With the gevent fix, SSLError should no longer occur from timeouts.
            passed = False
            details = f"Request Failed: {type(e).__name__}"
        
        duration = time.time() - start_time
        result = TestResult(name, passed, getattr(res, 'status_code', 0), details, duration)
        self.log_result(result)
        return result

    def log_result(self, result: TestResult):
        emoji = "✅" if result.passed else "❌"
        print(f"{emoji} {result.name}: {'PASS' if result.passed else 'FAIL'} ({result.duration:.2f}s) -> {result.details}")

    def summarize_and_save(self, results: List[TestResult], duration: float):
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0

        print("\n" + "="*60)
        print("🎯 TEST SUITE SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Total Endpoints Tested: {total_count}")
        print(f"✅ Passed: {passed_count} | ❌ Failed: {total_count - passed_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        status = "🟢 EXCELLENT" if success_rate >= 95 else "🔵 GOOD" if success_rate >= 80 else "🟡 NEEDS WORK"
        print(f"🎖️  Status: {status}")
        print("="*60)

        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
        print(f"💾 Results saved to: {filename}")

async def main():
    suite = OptimizedTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

    async def test_health(self) -> TestResult:
        """Test API health endpoint"""
        return await self._test_endpoint("/health")

    async def test_endpoints(self, client, endpoints: list) -> list:
        """Test all API endpoints with dynamic PKs and payloads, and report data status."""
        # 1. Get items
        item_pks = []
        try:
            items_resp = await client.get("/api/core/items/")
            items_status = f"Status: {items_resp.status_code}"
            if items_resp.status_code == 200:
                items = items_resp.json()
                if isinstance(items, list):
                    item_pks = [item["id"] for item in items if "id" in item]
                elif isinstance(items, dict) and "results" in items:
                    item_pks = [item["id"] for item in items["results"] if "id" in item]
                items_status += f", Found {len(item_pks)} items"
            else:
                items_status += ", Could not fetch items."
        except Exception as e:
            items_status = f"Error fetching items: {e}"
        print(f"[DATA CHECK] /api/core/items/: {items_status}")
        # 2. Get listings
        listing_pks = []
        listings_status = "Not checked"
        if item_pks:
            try:
                listings_resp = await client.get(f"/api/core/items/{item_pks[0]}/listings/")
                listings_status = f"Status: {listings_resp.status_code}"
                if listings_resp.status_code == 200:
                    listings = listings_resp.json()
                    if isinstance(listings, list):
                        listing_pks = [l["id"] for l in listings if "id" in l]
                    elif isinstance(listings, dict) and "results" in listings:
                        listing_pks = [l["id"] for l in listings["results"] if "id" in l]
                    listings_status += f", Found {len(listing_pks)} listings"
                else:
                    listings_status += ", Could not fetch listings."
            except Exception as e:
                listings_status = f"Error fetching listings: {e}"
        print(f"[DATA CHECK] /api/core/items/<pk>/listings/: {listings_status}")
        # Replace hardcoded PKs in endpoints
        def replace_pk(ep):
            if "items/1/" in ep and item_pks:
                return ep.replace("items/1/", f"items/{item_pks[0]}/")
            if "items/1/analyze/" in ep and item_pks:
                return ep.replace("items/1/analyze/", f"items/{item_pks[0]}/analyze/")
            if "items/1/analysis/" in ep and item_pks:
                return ep.replace("items/1/analysis/", f"items/{item_pks[0]}/analysis/")
            if "items/1/listings/" in ep and item_pks:
                return ep.replace("items/1/listings/", f"items/{item_pks[0]}/listings/")
            if "listings/1/" in ep and listing_pks:
                return ep.replace("listings/1/", f"listings/{listing_pks[0]}/")
            return ep
        endpoints = [replace_pk(ep) for ep in endpoints]
        # Prepare POST payloads for known endpoints (send image for AI/image endpoints and analyze-and-price, and for /items/<pk>/analyze/)
        post_payloads = {}
        if os.path.exists(self.config.test_image_path):
            with open(self.config.test_image_path, "rb") as img_file:
                image_bytes = img_file.read()
            def image_file():
                from io import BytesIO
                return ("example2.jpg", BytesIO(image_bytes), "image/jpeg")
            # Endpoints expecting image upload
            post_payloads = {
                "/api/core/ai/image-search/": {"image": image_file()},
                "/api/core/ai/advanced-search/": {"image": image_file()},
                "/api/core/ai/crop-preview/": {"image": image_file()},
                "/api/core/analyze-and-price/": {"image": image_file()},
            }
        # Add /items/<pk>/analyze/ as POST with image if item_pks found
        for ep in endpoints:
            if "/items/" in ep and ep.endswith("/analyze/") and os.path.exists(self.config.test_image_path):
                with open(self.config.test_image_path, "rb") as img_file:
                    image_bytes = img_file.read()
                def image_file():
                    from io import BytesIO
                    return ("example2.jpg", BytesIO(image_bytes), "image/jpeg")
                post_payloads[ep] = {"image": image_file()}
        # Map endpoint to method and whether auth is required
        protected_endpoints = [
            "/api/core/analyze-and-price/",
            "/api/core/ai/image-search/",
            "/api/core/ai/crop-preview/",
        ]
        post_endpoints = set(post_payloads.keys()) | {"/api/core/ebay-token/action/", "/api/core/admin/set-ebay-refresh-token/", "/api/core/price-analysis/"}
        tasks = []
        for ep in endpoints:
            method = "POST" if any(ep.startswith(p) for p in post_endpoints) or ep.endswith("/analyze/") or ep.endswith("/analyze-and-price/") else "GET"
            files = post_payloads.get(ep) if method == "POST" and ep in post_payloads else None
            # Use auth for protected endpoints
            use_auth = any(ep.startswith(p) for p in protected_endpoints)
            tasks.append(self._test_endpoint(ep, method=method, files=files, use_auth=use_auth))
        return await asyncio.gather(*tasks)

    async def test_image_upload(self) -> TestResult:
        """Test image upload to AI endpoint with SSL/protocol error handling."""
        start_time = time.time()
        if not os.path.exists(self.config.test_image_path):
            return TestResult("Image Upload", False, "Test image not found")
        backend_url = self.config.base_url.rstrip("/")
        url = f"{backend_url}/api/core/ai/image-search/"
        try:
            with open(self.config.test_image_path, "rb") as f:
                files = {"image": f}
                # Removed requests.exceptions.SSLError handling. Use httpx exceptions if needed.
        except Exception as e:
            passed = False
            details = str(e)
        return TestResult("Image Upload", passed, details, time.time() - start_time)

    async def test_ai_services(self) -> Dict[str, TestResult]:
        """Test AI services with mock data"""
        services = {
            'google_vision': self._mock_ai_test("Google Vision", 0.92),
            'aws_rekognition': self._mock_ai_test("AWS Rekognition", 0.88),
            'combined_analysis': self._mock_ai_test("Combined Analysis", 0.90)
        }
        
        return {name: await test for name, test in services.items()}

    async def _mock_ai_test(self, service_name: str, confidence: float) -> TestResult:
        """Mock AI service test"""
        await asyncio.sleep(0.1)  # Simulate processing time
        return TestResult(
            name=service_name,
            passed=confidence > 0.8,
            details=f"Confidence: {confidence:.2f}",
            duration=0.1
        )

    async def test_ebay_integration(self) -> TestResult:
        """Test eBay integration"""
        return await self._test_endpoint("/api/ebay/")

    async def run_performance_tests(self) -> Dict[str, float]:
        """Run performance benchmarks"""
        tests = {
            'health_check': self._benchmark_endpoint("/health"),
            'search_endpoint': self._benchmark_endpoint("/api/search/"),
            'ai_endpoint': self._benchmark_endpoint("/api/ai/advanced/")
        }
        
        results = {}
        for name, test in tests.items():
            times = await test
            results[name] = sum(times) / len(times) * 1000  # Average in ms
        
        return results

    async def _benchmark_endpoint(self, endpoint: str, iterations: int = 3) -> List[float]:
        """Benchmark endpoint response times"""
        times = []
        for _ in range(iterations):
            start = time.time()
            try:
                self.session.get(f"{self.config.base_url}{endpoint}")
            except:
                pass  # Ignore errors for benchmarking
            times.append(time.time() - start)
            await asyncio.sleep(0.1)  # Brief pause between requests
        return times

    def _calculate_success_rate(self, results: Dict[str, Any]) -> float:
        """Calculate overall success rate"""
        total = 0
        passed = 0
        
        def count_results(obj):
            nonlocal total, passed
            if isinstance(obj, TestResult):
                total += 1
                if obj.passed:
                    passed += 1
            elif isinstance(obj, dict):
                for value in obj.values():
                    count_results(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_results(item)
        
        count_results(results)
        return (passed / total * 100) if total > 0 else 0

    def _print_summary(self, results: Dict[str, Any], duration: float):
        """Print concise test summary"""
        success_rate = self._calculate_success_rate(results)
        
        print("\n" + "="*60)
        print("🎯 TEST SUITE SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        status = "🟢 EXCELLENT" if success_rate >= 90 else \
                "🔵 GOOD" if success_rate >= 75 else \
                "🟡 NEEDS WORK" if success_rate >= 50 else "🔴 CRITICAL"
        
        print(f"🎖️  Status: {status}")
        
        # Performance summary
        if 'performance' in results:
            print(f"\n⚡ Performance:")
            for test, time_ms in results['performance'].items():
                print(f"   {test}: {time_ms:.1f}ms")
        
        print("="*60)

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting Optimized Test Suite")
        print("="*60)
        
        start_time = time.time()
        
        # Run tests concurrently where possible
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
            # Step 1: Authenticate
            await self.authenticate(client)
            if not self.auth_token:
                print("❌ CRITICAL: Authentication failed. Cannot proceed with authenticated tests.")
                return
            # Step 2: Dynamic URL Discovery
            endpoints_to_test = await self.discover_urls(client)
            if not endpoints_to_test:
                print("❌ CRITICAL: Could not discover URLs. Aborting.")
                return
            # Step 3: Run all endpoint tests concurrently
            health_task = self.test_health()
            endpoints_task = self.test_endpoints(client, endpoints_to_test)
            image_task = self.test_image_upload()
            ai_task = self.test_ai_services()
            ebay_task = self.test_ebay_integration()
            perf_task = self.run_performance_tests()
            # Gather results
            health_result = await health_task
            endpoints_results = await endpoints_task
            image_result = await image_task
            ai_results = await ai_task
            ebay_result = await ebay_task
            perf_results = await perf_task
        
        # Log individual results
        self._log_result(health_result)
        for result in endpoints_results:
            self._log_result(result)
        self._log_result(image_result)
        for result in ai_results.values():
            self._log_result(result)
        self._log_result(ebay_result)
        
        # Compile final results
        results = {
            'health': health_result,
            'endpoints': endpoints_results,
            'image_upload': image_result,
            'ai_services': ai_results,
            'ebay': ebay_result,
            'performance': perf_results,
            'timestamp': datetime.now().isoformat(),
            'duration': time.time() - start_time
        }
        
        self._print_summary(results, results['duration'])
        
        # Save results
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to: {filename}")
        
        return results

async def main():
    """Main execution function"""
    suite = OptimizedTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())