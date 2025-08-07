#!/usr/bin/env python3
import requests
import json

response = requests.get('https://restyleproject-production.up.railway.app/core/ai/status/')
data = response.json()

print('🔍 AI SERVICES DETAILED STATUS:')
print('='*40)

services = data.get('services', {})
available = []
not_available = []

for service_name, is_available in services.items():
    if is_available:
        available.append(service_name)
    else:
        not_available.append(service_name)

print('✅ AVAILABLE SERVICES:')
for service in available:
    print(f'   • {service}')

print('\n❌ NOT AVAILABLE SERVICES:')
for service in not_available:
    print(f'   • {service}')

print(f'\nTotal: {len(available)}/{len(services)} services available')
