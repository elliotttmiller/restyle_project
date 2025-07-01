#!/usr/bin/env python3
import socket

def check_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            s.close()
            return True
    except OSError as e:
        print(f"Port {port} error: {e}")
        return False

# Test ports
print("Testing port availability:")
for port in [8000, 8001, 8002, 3000]:
    available = check_port_available(port)
    print(f"Port {port}: {'Available' if available else 'Not available'}") 