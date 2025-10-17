# Performance Optimization Guide

## Overview
This guide outlines performance optimization strategies and best practices for the Restyle.ai platform.

## 🚀 Backend Performance

### Database Optimization

#### 1. Query Optimization
```python
# Bad: N+1 queries
for item in Item.objects.all():
    print(item.user.username)

# Good: Use select_related for foreign keys
items = Item.objects.select_related('user').all()
for item in items:
    print(item.user.username)

# Good: Use prefetch_related for many-to-many
items = Item.objects.prefetch_related('listings').all()
```

#### 2. Add Database Indexes
```python
# models.py
class Item(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'created_at']),
            models.Index(fields=['-created_at']),
        ]
```

#### 3. Use Database Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Caching Strategy

#### 1. Redis Caching
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'restyle',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Usage in views
from django.core.cache import cache

def get_items(request):
    cache_key = f'items_user_{request.user.id}'
    items = cache.get(cache_key)
    
    if items is None:
        items = Item.objects.filter(user=request.user).select_related('user')
        cache.set(cache_key, items, timeout=300)
    
    return items
```

#### 2. View Caching
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def item_list(request):
    items = Item.objects.all()
    return render(request, 'items/list.html', {'items': items})
```

#### 3. Template Fragment Caching
```django
{% load cache %}
{% cache 500 sidebar request.user.username %}
    .. sidebar for logged in user ..
{% endcache %}
```

### API Optimization

#### 1. Pagination
```python
# Already implemented in settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

#### 2. Serializer Optimization
```python
# Use only() and defer() to limit database fields
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price']  # Only necessary fields
    
    def to_representation(self, instance):
        # Optimize nested serializers
        return super().to_representation(instance)
```

#### 3. Async Views (Django 4.2+)
```python
async def async_view(request):
    data = await some_async_operation()
    return JsonResponse({'data': data})
```

### Background Task Optimization

#### 1. Celery Task Optimization
```python
# tasks.py
from celery import Task

class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        # Cleanup after success
        pass
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Handle failure
        pass

@shared_task(bind=True, base=CallbackTask)
def process_image(self, image_path):
    # Process image asynchronously
    pass
```

#### 2. Task Prioritization
```python
# High priority tasks
@shared_task(priority=0)
def critical_task():
    pass

# Low priority tasks
@shared_task(priority=9)
def batch_task():
    pass
```

### Image Processing Optimization

#### 1. Lazy Loading
```python
from PIL import Image
from io import BytesIO

def optimize_image(image_file, max_size=(800, 800)):
    img = Image.open(image_file)
    img.thumbnail(max_size, Image.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    return output
```

#### 2. Image CDN
```python
# Use CloudFront, CloudFlare, or similar CDN for images
MEDIA_URL = 'https://cdn.yourdomain.com/media/'
```

## 📱 Mobile App Performance

### React Native Optimization

#### 1. FlatList Optimization
```javascript
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={item => item.id}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>
```

#### 2. Image Optimization
```javascript
import { Image } from 'expo-image';

<Image
  source={{ uri: imageUrl }}
  contentFit="cover"
  transition={200}
  cachePolicy="memory-disk"
/>
```

#### 3. Memoization
```javascript
import { useMemo, useCallback } from 'react';

function MyComponent({ items }) {
  const sortedItems = useMemo(
    () => items.sort((a, b) => a.price - b.price),
    [items]
  );
  
  const handlePress = useCallback((item) => {
    console.log(item);
  }, []);
  
  return <ItemList items={sortedItems} onPress={handlePress} />;
}
```

#### 4. Code Splitting
```javascript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Bundle Size Optimization

#### 1. Analyze Bundle Size
```bash
npx expo-bundle-analyzer
```

#### 2. Remove Unused Dependencies
```bash
npm prune
npm dedupe
```

#### 3. Use Production Build
```bash
expo build:ios --release-channel production
expo build:android --release-channel production
```

## 🌐 Frontend Performance

### React Web Optimization

#### 1. Code Splitting with React.lazy
```javascript
import React, { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Suspense>
  );
}
```

#### 2. Image Optimization
```javascript
import { LazyLoadImage } from 'react-lazy-load-image-component';

<LazyLoadImage
  src={imageUrl}
  alt="Item"
  effect="blur"
  threshold={100}
/>
```

#### 3. Virtual Scrolling
```javascript
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

## 🔧 Infrastructure Optimization

### Docker Optimization

#### 1. Multi-stage Builds
```dockerfile
# Build stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "backend.wsgi:application"]
```

#### 2. Layer Caching
```dockerfile
# Copy only requirements first for better caching
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Then copy application code
COPY . /app/
```

### Nginx Optimization

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

# Enable browser caching
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Enable keep-alive
keepalive_timeout 65;
keepalive_requests 100;
```

## 📊 Monitoring & Profiling

### Django Debug Toolbar (Development)
```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Django Silk (Profiling)
```python
# Monitor request/response times
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

### New Relic / DataDog (Production)
```python
# Application Performance Monitoring
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
```

## 🎯 Performance Targets

### Backend API
- **Response Time**: < 200ms (p95)
- **Throughput**: 1000+ requests/second
- **Database Query Time**: < 50ms (average)
- **Cache Hit Rate**: > 80%

### Mobile App
- **Time to Interactive**: < 3 seconds
- **Bundle Size**: < 5MB
- **Memory Usage**: < 100MB
- **Frame Rate**: 60 FPS

### Frontend Web
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 3.5 seconds
- **Lighthouse Score**: > 90

## 🔍 Performance Testing

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 100 http://localhost:8000/api/items/

# Using Locust
locust -f locustfile.py --host=http://localhost:8000
```

### Frontend Testing
```bash
# Lighthouse
npm install -g lighthouse
lighthouse http://localhost:3000 --view

# WebPageTest
# Use webpagetest.org for detailed analysis
```

## 📚 Additional Resources

- [Django Performance Tips](https://docs.djangoproject.com/en/stable/topics/performance/)
- [React Performance Optimization](https://reactjs.org/docs/optimizing-performance.html)
- [React Native Performance](https://reactnative.dev/docs/performance)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Best Practices](https://redis.io/topics/optimization)
