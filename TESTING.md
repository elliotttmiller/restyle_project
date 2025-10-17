# Testing Guide

## Overview
Comprehensive testing strategy for Restyle.ai covering unit tests, integration tests, and end-to-end testing.

## 🧪 Backend Testing (Django)

### Test Setup

#### Install Testing Dependencies
```bash
pip install pytest pytest-django pytest-cov factory-boy faker
```

#### Configure pytest (pytest.ini)
```ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
```

### Unit Tests

#### Model Tests
```python
# backend/core/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model
from core.models import Item, Listing

User = get_user_model()

@pytest.mark.django_db
class TestItemModel:
    def test_create_item(self):
        user = User.objects.create_user(username='test', password='test123')
        item = Item.objects.create(
            name='Test Item',
            user=user,
            price=29.99
        )
        assert item.name == 'Test Item'
        assert item.user == user
        assert item.price == 29.99
    
    def test_item_string_representation(self):
        user = User.objects.create_user(username='test', password='test123')
        item = Item.objects.create(name='Test Item', user=user)
        assert str(item) == 'Test Item'
```

#### View Tests
```python
# backend/core/tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

@pytest.mark.django_db
class TestItemViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_items(self):
        url = reverse('item-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_item(self):
        url = reverse('item-list')
        data = {'name': 'New Item', 'price': 49.99}
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Item'
```

#### Service Tests
```python
# backend/core/tests/test_ai_service.py
import pytest
from unittest.mock import Mock, patch
from core.ai_service import AIService

@pytest.mark.django_db
class TestAIService:
    def setup_method(self):
        self.ai_service = AIService()
    
    @patch('core.ai_service.vision.ImageAnnotatorClient')
    def test_analyze_image(self, mock_vision_client):
        # Mock Google Vision API response
        mock_response = Mock()
        mock_response.label_annotations = [
            Mock(description='shirt', score=0.95),
            Mock(description='clothing', score=0.90),
        ]
        mock_vision_client.return_value.label_detection.return_value = mock_response
        
        result = self.ai_service.analyze_image(b'fake_image_data')
        
        assert 'labels' in result
        assert len(result['labels']) > 0
```

### Integration Tests

```python
# backend/core/tests/test_integration.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
class TestImageAnalysisFlow:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user('test', password='test123')
        self.client.force_authenticate(user=self.user)
    
    def test_complete_image_analysis_flow(self):
        # 1. Upload image
        url = '/api/core/ai/image-search/'
        with open('test_image.jpg', 'rb') as img:
            response = self.client.post(url, {'image': img})
        
        assert response.status_code == 200
        assert 'analysis' in response.data
        
        # 2. Verify results saved
        item_id = response.data.get('item_id')
        assert item_id is not None
        
        # 3. Retrieve analysis
        detail_url = f'/api/core/items/{item_id}/'
        response = self.client.get(detail_url)
        assert response.status_code == 200
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/core/tests/test_models.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run parallel tests
pytest -n auto

# Run specific test
pytest backend/core/tests/test_views.py::TestItemViews::test_list_items

# Run tests matching pattern
pytest -k "test_create"
```

## 🎭 Frontend Testing (React)

### Test Setup

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event jest-environment-jsdom
```

### Component Tests

```javascript
// frontend/src/components/__tests__/SearchBar.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '../SearchBar';

describe('SearchBar Component', () => {
  test('renders search input', () => {
    render(<SearchBar />);
    const input = screen.getByPlaceholderText(/search/i);
    expect(input).toBeInTheDocument();
  });
  
  test('handles search input', () => {
    const handleSearch = jest.fn();
    render(<SearchBar onSearch={handleSearch} />);
    
    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: 'shirt' } });
    
    expect(input.value).toBe('shirt');
  });
  
  test('submits search on button click', () => {
    const handleSearch = jest.fn();
    render(<SearchBar onSearch={handleSearch} />);
    
    const input = screen.getByPlaceholderText(/search/i);
    const button = screen.getByRole('button');
    
    fireEvent.change(input, { target: { value: 'shirt' } });
    fireEvent.click(button);
    
    expect(handleSearch).toHaveBeenCalledWith('shirt');
  });
});
```

### Hook Tests

```javascript
// frontend/src/hooks/__tests__/useItems.test.js
import { renderHook, act } from '@testing-library/react';
import useItems from '../useItems';

describe('useItems Hook', () => {
  test('fetches items', async () => {
    const { result } = renderHook(() => useItems());
    
    expect(result.current.loading).toBe(true);
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.items).toBeDefined();
  });
});
```

### Integration Tests

```javascript
// frontend/src/__tests__/integration/ItemFlow.test.js
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../App';

describe('Item Management Flow', () => {
  test('complete item creation flow', async () => {
    render(<App />);
    
    // Navigate to create item page
    const createButton = screen.getByText(/add item/i);
    userEvent.click(createButton);
    
    // Fill form
    const nameInput = screen.getByLabelText(/item name/i);
    userEvent.type(nameInput, 'Test Item');
    
    const priceInput = screen.getByLabelText(/price/i);
    userEvent.type(priceInput, '29.99');
    
    // Submit
    const submitButton = screen.getByRole('button', { name: /submit/i });
    userEvent.click(submitButton);
    
    // Verify success
    await waitFor(() => {
      expect(screen.getByText(/item created/i)).toBeInTheDocument();
    });
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test SearchBar.test.js

# Run in watch mode
npm test -- --watch
```

## 📱 Mobile Testing (React Native)

### Setup

```bash
npm install --save-dev jest @testing-library/react-native
```

### Component Tests

```javascript
// restyle-mobile/app/__tests__/Dashboard.test.js
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Dashboard from '../(app)/dashboard';

describe('Dashboard Component', () => {
  test('renders correctly', () => {
    const { getByText } = render(<Dashboard />);
    expect(getByText('Restyle.ai')).toBeTruthy();
  });
  
  test('shows loading state during analysis', () => {
    const { getByText } = render(<Dashboard />);
    const button = getByText('Select Image to Analyze');
    fireEvent.press(button);
    
    // Should show loading indicator
    expect(getByText(/analyzing/i)).toBeTruthy();
  });
});
```

### Store Tests

```javascript
// restyle-mobile/shared/__tests__/resultsStore.test.js
import { renderHook, act } from '@testing-library/react-hooks';
import useResultsStore from '../resultsStore';

describe('Results Store', () => {
  test('starts analysis and updates state', async () => {
    const { result } = renderHook(() => useResultsStore());
    
    const mockImage = { uri: 'file://test.jpg' };
    
    await act(async () => {
      await result.current.startAnalysis(mockImage);
    });
    
    expect(result.current.isLoading).toBe(false);
  });
  
  test('handles errors correctly', async () => {
    const { result } = renderHook(() => useResultsStore());
    
    await act(async () => {
      await result.current.startAnalysis(null);
    });
    
    expect(result.current.error).toBeTruthy();
  });
});
```

## 🔄 End-to-End Testing

### Playwright Setup

```bash
npm install -D @playwright/test
npx playwright install
```

### E2E Tests

```javascript
// e2e/tests/item-management.spec.js
import { test, expect } from '@playwright/test';

test.describe('Item Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.click('text=Login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'testpass');
    await page.click('button[type="submit"]');
  });
  
  test('create new item', async ({ page }) => {
    await page.click('text=Add Item');
    await page.fill('[name="name"]', 'Test Item');
    await page.fill('[name="price"]', '29.99');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=Test Item')).toBeVisible();
  });
  
  test('search for items', async ({ page }) => {
    await page.fill('[placeholder="Search"]', 'shirt');
    await page.click('button[aria-label="Search"]');
    
    await expect(page.locator('.item-card')).toHaveCount(1);
  });
});
```

## 🔐 Security Testing

### OWASP ZAP Scanning

```bash
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000 \
  -r zap-report.html
```

### Bandit Security Scan

```bash
bandit -r backend/ -ll -x tests,migrations
```

### Dependency Vulnerability Scanning

```bash
# Python
pip install safety
safety check

# JavaScript
npm audit
npm audit fix
```

## 📊 Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class RestyleUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def list_items(self):
        self.client.get("/api/items/")
    
    @task(3)
    def view_item(self):
        self.client.get("/api/items/1/")
    
    @task(2)
    def search_items(self):
        self.client.post("/api/search/", json={
            "query": "shirt"
        })
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Frontend Performance Testing

```javascript
// Test with Lighthouse CI
npm install -g @lhci/cli

lhci autorun --collect.url=http://localhost:3000
```

## 🎯 Test Coverage Goals

### Coverage Targets
- **Backend**: 80%+ coverage
- **Frontend**: 70%+ coverage  
- **Mobile**: 70%+ coverage
- **Critical paths**: 100% coverage

### Generate Coverage Reports

```bash
# Backend
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Frontend
npm test -- --coverage
open coverage/lcov-report/index.html

# Combined report
coverage combine
coverage html
```

## 🔄 Continuous Testing

### Pre-commit Testing

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### CI/CD Integration

Already configured in `.github/workflows/ci.yml`

## 📋 Testing Checklist

### Before Every Commit
- [ ] Run unit tests
- [ ] Check code coverage
- [ ] Run linting
- [ ] Fix any failing tests

### Before Every PR
- [ ] All tests pass
- [ ] Coverage meets targets
- [ ] Integration tests pass
- [ ] No security vulnerabilities

### Before Deployment
- [ ] Full test suite passes
- [ ] E2E tests pass
- [ ] Performance tests pass
- [ ] Security scan completed
- [ ] Load testing completed

## 📚 Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use factories** for test data
4. **Mock external services** (APIs, databases)
5. **Test edge cases** and error conditions
6. **Maintain test documentation**
7. **Review test coverage** regularly
8. **Run tests in CI/CD** pipeline
9. **Keep tests fast** (<5 minutes total)
10. **Test critical paths** thoroughly

## 🆘 Troubleshooting

### Common Issues

**Tests fail locally but pass in CI**
- Check environment differences
- Verify database state
- Check file paths

**Slow tests**
- Use pytest-xdist for parallel execution
- Mock external API calls
- Use in-memory databases for tests

**Flaky tests**
- Add explicit waits
- Avoid time-based assertions
- Check for race conditions

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [React Testing Tutorial](https://reactjs.org/docs/testing.html)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
