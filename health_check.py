"""
Health Check Script - Verify application status

This script checks if both servers are running and responsive.
Run this regularly to monitor application health.
"""
import requests
import sys
from datetime import datetime
from pathlib import Path
from logger import setup_logger

logger = setup_logger(__name__)

FLASK_URL = "http://127.0.0.1:5000/health"
FASTAPI_URL = "http://127.0.0.1:8000/health"
TIMEOUT = 5

def check_service(url: str, service_name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"✓ {service_name}: HEALTHY")
            return True
        else:
            print(f"❌ {service_name}: Unhealthy (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name}: Connection failed (refused)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {service_name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {service_name}: Error - {e}")
        return False

def check_all():
    """Check all services"""
    print("=" * 60)
    print(f"Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Check Flask
    flask_ok = check_service(FLASK_URL, "Flask Frontend")
    
    # Check FastAPI
    fastapi_ok = check_service(FASTAPI_URL, "FastAPI Backend")
    
    print()
    
    if flask_ok and fastapi_ok:
        print("✓ All services are healthy")
        return 0
    elif flask_ok or fastapi_ok:
        print("⚠ Some services are down")
        return 1
    else:
        print("❌ All services are down")
        return 1

if __name__ == "__main__":
    sys.exit(check_all())
