
def parse_args():
    pass

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
from typing import List, Dict, Any
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

import logging
import sys

import uuid

class OptimizedTestSuite:
    def __init__(self):
        self.config = TestConfig()
        self.auth_token = None
        # Advanced diagnostics and logging
        log_filename = f"debug_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.run_id = str(uuid.uuid4())
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        # Patch: Set encoding to utf-8 for Windows terminals to support emoji/unicode
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except AttributeError:
            import io
            handler.stream = io.TextIOWrapper(handler.stream.buffer, encoding='utf-8', errors='replace')
        self.logger = logging.getLogger("OptimizedTestSuite")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Test Suite Run ID: %s", self.run_id)
        self.logger.info("Test Suite Configuration: %s", self.config)
        self.logger.info("Python version: %s", os.sys.version)
        self.logger.info("Environment variables summary: %s", {k: v for k, v in os.environ.items() if k.startswith('RAILWAY') or k.startswith('TEST_') or k.startswith('DJANGO')})
        if not self.config.verify_ssl:
            self.logger.warning("⚠️  SSL verification is disabled.")

    async def run_all_tests(self):
        self.logger.info("🚀 Starting Optimized & Self-Adapting Test Suite")
        start_time = time.time()
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
            await self.authenticate(client)
            if not self.auth_token:
                self.logger.critical("❌ CRITICAL: Authentication failed. Cannot proceed with authenticated tests.")
                return
            endpoints_to_test = await self.discover_urls(client)
            if not endpoints_to_test:
                self.logger.critical("❌ CRITICAL: Could not discover URLs. Aborting.")
                return
            tasks = [self.test_endpoint(client, endpoint) for endpoint in endpoints_to_test]
            results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        self.summarize_and_save(results, duration)

    async def authenticate(self, client: httpx.AsyncClient):
        self.logger.info(f"Attempting authentication for user: {self.config.test_user}")
        try:
            res = await client.post("/api/token/", json={"username": self.config.test_user, "password": self.config.test_pass})
            self.logger.debug(f"Auth request: POST /api/token/ payload={{'username': '{self.config.test_user}', 'password': '***'}}")
            self.logger.debug(f"Auth response: status={res.status_code}, body={res.text}")
            res.raise_for_status()
            self.auth_token = res.json()["access"]
            self.logger.info(f"🔑 Obtained JWT token for '{self.config.test_user}'")
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            self.logger.error(f"Authentication failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Auth failure response: status={e.response.status_code}, body={e.response.text}")
            self.auth_token = None

    async def discover_urls(self, client: httpx.AsyncClient) -> List[str]:
        self.logger.info("\n🔍 Discovering URLs from the server...")
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            res = await client.get("/api/core/internal/list-urls/", headers=headers)
            self.logger.debug(f"GET /api/core/internal/list-urls/ headers={headers}")
            self.logger.debug(f"Response: status={res.status_code}, body={res.text}")
            if res.status_code == 200:
                urls = [item['path'] for item in res.json()]
                urls = [u for u in urls if not u.startswith('admin/') and not u.startswith('api/core/internal/')]
                self.logger.info(f"✅ Discovered {len(urls)} endpoints to test.")
                return urls
            if res.status_code == 403:
                self.logger.error(f"❌ URL Discovery failed with status 403 (Forbidden). User '{self.config.test_user}' may lack admin privileges. Suggestion: Ensure this user is a superuser.")
            else:
                self.logger.error(f"❌ URL Discovery failed with status {res.status_code}")
            return []
        except httpx.RequestError as e:
            self.logger.error(f"❌ URL Discovery request failed: {e}")
            return []

    async def test_endpoint(self, client: httpx.AsyncClient, endpoint_path: str) -> TestResult:
        start_time = time.time()
        name = f"Endpoint: {endpoint_path}"
        is_post = False
        use_auth = False
        payload = {}
        correlation_id = str(uuid.uuid4())
        protected_patterns = ['/analyze-and-price/']
        if any(p in endpoint_path for p in protected_patterns):
            use_auth = True
        headers = {"X-Correlation-ID": correlation_id}
        # Always send Authorization for /api/core/internal/list-urls/ if token is available
        if (use_auth and self.auth_token) or (endpoint_path == "/api/core/internal/list-urls/" and self.auth_token):
            headers["Authorization"] = f"Bearer {self.auth_token}"
        res = None
        # Patch: Use correct HTTP method for each endpoint
        post_endpoints = ["/api/users/register/", "/api/token/", "/api/token/refresh/", "/api/core/analyze-and-price/"]
        if endpoint_path in post_endpoints:
            method = "POST"
        else:
            method = "GET"
        payload = None
        request_kwargs = {}
        # Patch: Send correct payloads for each endpoint
        if endpoint_path == "/api/users/register/":
            request_kwargs["json"] = {"username": self.config.test_user, "password": self.config.test_pass}
        elif endpoint_path == "/api/token/":
            request_kwargs["json"] = {"username": self.config.test_user, "password": self.config.test_pass}
        elif endpoint_path == "/api/token/refresh/":
            # Use the last obtained refresh token if available
            refresh_token = getattr(self, "last_refresh_token", None)
            if refresh_token:
                request_kwargs["json"] = {"refresh": refresh_token}
            else:
                # Try to get a new refresh token first
                self.logger.info("Obtaining refresh token for /api/token/refresh/ test...")
                token_resp = await client.post("/api/token/", json={"username": self.config.test_user, "password": self.config.test_pass})
                if token_resp.status_code == 200:
                    refresh_token = token_resp.json().get("refresh")
                    self.last_refresh_token = refresh_token
                    request_kwargs["json"] = {"refresh": refresh_token}
                else:
                    self.logger.error("Failed to obtain refresh token for /api/token/refresh/ test.")
                    return TestResult(name, False, token_resp.status_code, "Could not obtain refresh token", 0)
        elif endpoint_path == "/api/core/analyze-and-price/":
            if os.path.exists(self.config.test_image_path):
                f = open(self.config.test_image_path, 'rb')
                files = {"image": (os.path.basename(self.config.test_image_path), f, "image/jpeg")}
                request_kwargs["files"] = files
                request_kwargs["_test_image_file"] = f  # keep reference for later closing
            else:
                self.logger.error(f"Test image not found at {self.config.test_image_path}")
                return TestResult(name, False, 0, "Test image not found", 0)
        try:
            self.logger.debug(f"[{correlation_id}] Request: {method} {endpoint_path} headers={headers} kwargs={list(request_kwargs.keys())}")
            req_time = time.time()
            # For analyze-and-price, ensure file stays open during request
            try:
                res = await client.request(method, endpoint_path, headers=headers, **{k: v for k, v in request_kwargs.items() if k != "_test_image_file"})
            finally:
                if "_test_image_file" in request_kwargs:
                    request_kwargs["_test_image_file"].close()
            resp_time = time.time()
            elapsed = resp_time - req_time
            self.logger.debug(f"[{correlation_id}] Response: status={res.status_code}, body={res.text}, elapsed={elapsed:.3f}s")
            if res.status_code >= 400:
                self.logger.error(f"[{correlation_id}] ERROR RESPONSE BODY for {endpoint_path}: {res.text}")
            # Save refresh token if present
            if endpoint_path == "/api/token/" and res.status_code == 200:
                try:
                    self.last_refresh_token = res.json().get("refresh")
                except Exception:
                    pass
            passed = False
            details = f"Responded with Status {res.status_code}"
            if 200 <= res.status_code < 300:
                passed = True
            elif res.status_code == 401 and use_auth:
                passed = False
                details += " (FAIL: Unauthorized, check token)"
                self.logger.error(f"[{correlation_id}] 401 Unauthorized for {endpoint_path}. Token may be invalid or expired. Suggestion: Check if the token is expired or user credentials are correct.")
            elif res.status_code == 403:
                passed = False
                details += " (FAIL: Forbidden)"
                self.logger.error(f"[{correlation_id}] 403 Forbidden for {endpoint_path}. User '{self.config.test_user}' may lack required permissions. Suggestion: Ensure user is staff/superuser or has correct permissions.")
            elif res.status_code == 404:
                passed = False
                details += " (FAIL: Not Found)"
                self.logger.error(f"[{correlation_id}] 404 Not Found for {endpoint_path}. Suggestion: Check if the endpoint exists and is correctly spelled.")
        except httpx.RequestError as e:
            passed = False
            details = f"Request Failed: {type(e).__name__}"
            self.logger.error(f"[{correlation_id}] Request to {endpoint_path} failed: {e}")
        duration = time.time() - start_time
        result = TestResult(name, passed, getattr(res, 'status_code', 0), details, duration)
        self.log_result(result)
        return result

    def log_result(self, result: TestResult):
        emoji = "✅" if result.passed else "❌"
        msg = f"{emoji} {result.name}: {'PASS' if result.passed else 'FAIL'} ({result.duration:.2f}s) -> {result.details}"
        if result.passed:
            self.logger.info(msg)
        else:
            self.logger.error(msg)

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

    # The following methods were duplicated and/or broken and are removed to resolve syntax and runtime errors.
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