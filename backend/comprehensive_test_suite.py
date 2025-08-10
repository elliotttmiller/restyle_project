#!/usr/bin/env python3
"""
Final, Focused Comprehensive Test Suite for Restyle.ai
"""
import os
import json
import time
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

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

class FinalTestSuite:
    def __init__(self):
        self.config = TestConfig()
        self.auth_token = None
        if not self.config.verify_ssl:
            print("⚠️  SSL verification is disabled.")

    async def run_all_tests(self):
        print("🚀 Starting Final, Focused Test Suite")
        start_time = time.time()
        
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
            await self.authenticate(client)
            if not self.auth_token:
                print("❌ CRITICAL: Authentication failed. Aborting.")
                return

            tasks = [
                self.test_health_check(client),
                self.test_analyze_and_price(client),
            ]
            results = await asyncio.gather(*tasks)

        duration = time.time() - start_time
        self.summarize_and_save(results, duration)

    async def authenticate(self, client: httpx.AsyncClient):
        try:
            res = await client.post("/api/token/", json={"username": self.config.test_user, "password": self.config.test_pass})
            res.raise_for_status()
            self.auth_token = res.json()["access"]
            print(f"🔑 Obtained JWT token for '{self.config.test_user}'")
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            print(f"Authentication failed: {e}")

    async def test_health_check(self, client: httpx.AsyncClient) -> TestResult:
        """Tests the public health check endpoint."""
        start_time = time.time()
        name = "Endpoint: /api/core/health/"
        res = None
        try:
            res = await client.get("/api/core/health/")
            passed = res.status_code == 200
            details = f"Responded with Status {res.status_code}"
        except httpx.RequestError as e:
            passed = False
            details = f"Request Failed: {type(e).__name__}"
        
        duration = time.time() - start_time
        result = TestResult(name, passed, getattr(res, 'status_code', 0), details, duration)
        self.log_result(result)
        return result

    async def test_analyze_and_price(self, client: httpx.AsyncClient) -> TestResult:
        """Tests the primary AI analysis endpoint with an image upload."""
        start_time = time.time()
        name = "Endpoint: /api/core/analyze-and-price/"
        res = None
        
        if not os.path.exists(self.config.test_image_path):
            return TestResult(name, False, 0, "Test image not found", 0)

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            with open(self.config.test_image_path, 'rb') as f:
                files = {'image': (os.path.basename(self.config.test_image_path), f.read(), 'image/jpeg')}
                res = await client.post("/api/core/analyze-and-price/", headers=headers, files=files)
            
            passed = res.status_code == 200
            details = f"Responded with Status {res.status_code}"
            if not passed:
                details += f" | Body: {res.text[:200]}"

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
        print(f"✅ Passed: {passed_count} | ❌ Failed: {total_count - passed_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        status = "🟢 EXCELLENT" if success_rate == 100 else "🔴 CRITICAL"
        print(f"🎖️  Status: {status}")
        print("="*60)

        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
        print(f"💾 Results saved to: {filename}")

async def main():
    suite = FinalTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())