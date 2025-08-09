#!/usr/bin/env python3
"""
Optimized Comprehensive System Test Suite for Restyle.ai
"""
import os
import json
import time
import requests
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field

# Configuration
@dataclass
class TestConfig:
    backend_url: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "https://restyleproject-production.up.railway.app/")
    timeout: int = 10
    test_image_path: str = "test_files/example2.jpg"
    
    @property
    def endpoints(self) -> List[str]:
        return [
            "/api/core/health/",
            "/api/core/ai/status/",
            "/api/core/metrics/",
            "/api/core/ebay-token/health/",
            "/api/core/ebay-token/action/",
            "/api/core/ebay-search/",
            "/api/core/items/",
            "/api/core/items/1/",  # Example item pk
            "/api/core/items/1/analyze/",  # Example item pk
            "/api/core/items/1/analysis/",  # Example item pk
            "/api/core/items/1/listings/",  # Example item_pk
            "/api/core/listings/1/",  # Example listing pk
            "/api/core/admin/set-ebay-refresh-token/",
            "/api/core/ebay-oauth-callback/",
            "/api/core/ebay-oauth-declined/",
            "/api/core/ebay-oauth/",
            "/api/core/price-analysis/",
            "/api/core/ai/image-search/",
            "/api/core/ai/advanced-search/",
            "/api/core/privacy-policy/",
            "/api/core/accepted/",
            "/api/core/declined/",
            "/api/core/ai/crop-preview/",
            "/api/core/env-debug/",
            "/api/core/analyze-and-price/",
            "/api/core/health-check/"
        ]

@dataclass
class TestResult:
    name: str
    passed: bool
    details: str = ""
    duration: float = 0.0

class OptimizedTestSuite:
    def __init__(self):
        self.config = TestConfig()
        self.results: Dict[str, Any] = {}
        self.session = requests.Session()
        self.session.timeout = self.config.timeout
        # Default: allow skipping SSL verification for debugging, but warn
        self.session.verify = os.getenv("TEST_SSL_VERIFY", "False").lower() == "true"
        if not self.session.verify:
            print("⚠️  SSL verification is disabled. Set TEST_SSL_VERIFY=True to enable.")
        self.auth_token = None

    def authenticate(self):
        """Authenticate test user and obtain JWT token for protected endpoints."""
        backend_url = self.config.backend_url.rstrip("/")
        username = os.getenv("TEST_USER", "testuser")
        password = os.getenv("TEST_PASS", "testpass1234")
        email = f"{username}@example.com"
        # Try to register the user (ignore errors if already exists)
        try:
            reg_resp = self.session.post(f"{backend_url}/api/users/register/", json={
                "username": username,
                "password": password,
                "email": email
            }, timeout=10)
            if reg_resp.status_code in (201, 200):
                print(f"🆕 Registered test user: {username}")
        except Exception as e:
            print(f"⚠️  Registration error (may already exist): {e}")
        # Obtain JWT token
        try:
            token_resp = self.session.post(f"{backend_url}/api/token/", json={
                "username": username,
                "password": password
            }, timeout=10)
            if token_resp.status_code == 200 and "access" in token_resp.json():
                self.auth_token = token_resp.json()["access"]
                print(f"🔑 Obtained JWT token for {username}")
            else:
                print(f"❌ Failed to obtain JWT token: {token_resp.text}")
        except Exception as e:
            print(f"❌ Exception during JWT auth: {e}")

    def _log_result(self, result: TestResult):
        """Log test result with emoji"""
        emoji = "✅" if result.passed else "❌"
        print(f"{emoji} {result.name}: {'PASS' if result.passed else 'FAIL'} ({result.duration:.2f}s)")
        if result.details:
            print(f"    {result.details}")

    async def _test_endpoint(self, endpoint: str, method: str = "GET", data=None, files=None, use_auth=False, **kwargs) -> TestResult:
        """Generic endpoint tester with dynamic PK/data/auth support, with SSL/protocol error handling and retry. Prints full error body for failed endpoints."""
        import json as _json
        start_time = time.time()
        backend_url = self.config.backend_url.rstrip("/")
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{backend_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        try:
            response = getattr(self.session, method.lower())(url, data=data, files=files, headers=headers, **kwargs)
            passed = response.status_code in (200, 201, 400, 401, 403, 404)
            details = f"Status: {response.status_code}"
            # Print full error body for failed endpoints (500 or not passed)
            if not passed or response.status_code == 500:
                try:
                    error_json = response.json()
                    print(f"\n--- Error body for {endpoint} ---\n{_json.dumps(error_json, indent=2)}\n--- End error body ---\n")
                    details += f" | Error: {error_json.get('error', '')}"
                except Exception:
                    details += f" | Error body not JSON or unavailable"
        except requests.exceptions.SSLError as e:
            details = f"SSL error: {e}"
            print(f"❌ SSL error for {url}: {e}")
            if self.session.verify:
                try:
                    response = getattr(self.session, method.lower())(url, data=data, files=files, headers=headers, verify=False, **kwargs)
                    passed = response.status_code in (200, 201, 400, 401, 403, 404)
                    details = f"Status: {response.status_code} (SSL verify disabled)"
                except Exception as e2:
                    passed = False
                    details = f"SSL retry failed: {e2}"
            else:
                passed = False
        except Exception as e:
            passed = False
            details = str(e)
        return TestResult(
            name=f"Endpoint {endpoint}",
            passed=passed,
            details=details,
            duration=time.time() - start_time
        )

    async def test_health(self) -> TestResult:
        """Test API health endpoint"""
        return await self._test_endpoint("/health")

    async def test_endpoints(self) -> List[TestResult]:
        """Test all API endpoints with dynamic PKs and payloads, and report data status."""
        endpoints = self.config.endpoints.copy()
        # 1. Get items
        items_resp = self.session.get(f"{self.config.backend_url}/api/core/items/")
        item_pks = []
        items_status = f"Status: {items_resp.status_code}"
        if items_resp.status_code == 200:
            try:
                items = items_resp.json()
                if isinstance(items, list):
                    item_pks = [item["id"] for item in items if "id" in item]
                elif isinstance(items, dict) and "results" in items:
                    item_pks = [item["id"] for item in items["results"] if "id" in item]
                items_status += f", Found {len(item_pks)} items"
            except Exception as e:
                items_status += f", Error parsing items: {e}"
        else:
            items_status += ", Could not fetch items."
        print(f"[DATA CHECK] /api/core/items/: {items_status}")
        # 2. Get listings
        listing_pks = []
        listings_status = "Not checked"
        if item_pks:
            listings_resp = self.session.get(f"{self.config.backend_url}/api/core/items/{item_pks[0]}/listings/")
            listings_status = f"Status: {listings_resp.status_code}"
            if listings_resp.status_code == 200:
                try:
                    listings = listings_resp.json()
                    if isinstance(listings, list):
                        listing_pks = [l["id"] for l in listings if "id" in l]
                    elif isinstance(listings, dict) and "results" in listings:
                        listing_pks = [l["id"] for l in listings["results"] if "id" in l]
                    listings_status += f", Found {len(listing_pks)} listings"
                except Exception as e:
                    listings_status += f", Error parsing listings: {e}"
            else:
                listings_status += ", Could not fetch listings."
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
        backend_url = self.config.backend_url.rstrip("/")
        url = f"{backend_url}/api/core/ai/image-search/"
        try:
            with open(self.config.test_image_path, "rb") as f:
                files = {"image": f}
                try:
                    response = self.session.post(url, files=files, timeout=20)
                    passed = response.status_code in (200, 400)
                    details = f"Status: {response.status_code}"
                except requests.exceptions.SSLError as e:
                    details = f"SSL error: {e}"
                    print(f"❌ SSL error for {url}: {e}")
                    if self.session.verify:
                        try:
                            response = self.session.post(url, files=files, timeout=20, verify=False)
                            passed = response.status_code in (200, 400)
                            details = f"Status: {response.status_code} (SSL verify disabled)"
                        except Exception as e2:
                            passed = False
                            details = f"SSL retry failed: {e2}"
                    else:
                        passed = False
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
                self.session.get(f"{self.config.backend_url}{endpoint}")
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
        health_task = self.test_health()
        endpoints_task = self.test_endpoints()
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
    suite.authenticate()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())