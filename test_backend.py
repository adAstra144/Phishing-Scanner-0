#!/usr/bin/env python3
"""
Test script for the Anti-Phishing Scanner backend
"""

import requests
import json
import time

def test_backend():
    """Test the backend API endpoints"""
    
    # Base URL - change this to your Hugging Face Space URL when deployed
    base_url = "http://localhost:7860"
    
    print("🔍 Testing Anti-Phishing Scanner Backend")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 2: Home endpoint
    print("\n2. Testing Home endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Home endpoint: {data}")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
    
    # Test 3: Analyze endpoint with phishing example
    print("\n3. Testing Analyze endpoint (Phishing example)...")
    phishing_message = "Your account has been suspended. Click here to verify immediately."
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json={"message": phishing_message},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phishing Analysis: {data}")
        else:
            print(f"❌ Phishing analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Phishing analysis error: {e}")
    
    # Test 4: Analyze endpoint with safe example
    print("\n4. Testing Analyze endpoint (Safe example)...")
    safe_message = "Thank you for your order. Your confirmation number is 12345."
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json={"message": safe_message},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Safe Analysis: {data}")
        else:
            print(f"❌ Safe analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Safe analysis error: {e}")
    
    # Test 5: Error handling
    print("\n5. Testing Error handling...")
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json={},  # Missing message field
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Error handling: Correctly rejected missing message")
        else:
            print(f"❌ Error handling: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

def test_local_backend():
    """Test the backend running locally"""
    print("🚀 Starting local backend test...")
    
    # Start the backend (this will run in the background)
    import subprocess
    import sys
    
    try:
        # Start the backend
        process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for the backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(10)
        
        # Test the backend
        test_backend()
        
        # Stop the backend
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"❌ Error running local test: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        test_local_backend()
    else:
        test_backend() 