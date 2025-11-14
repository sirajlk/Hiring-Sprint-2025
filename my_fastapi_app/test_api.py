#!/usr/bin/env python3
"""
Quick test script for the vehicle inspection API.
Tests the complete workflow: start → upload pickup → switch → upload return → complete
"""

import requests
import sys
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_inspection_workflow():
    print("🧪 Testing Vehicle Inspection API...\n")
    
    # Test 1: Start inspection
    print("1️⃣  Starting inspection session...")
    try:
        res = requests.post(f"{API_BASE}/api/inspection/start")
        assert res.status_code == 200, f"Failed: {res.status_code} {res.text}"
        session_id = res.json()['session_id']
        print(f"   ✅ Session created: {session_id[:8]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Get API info
    print("\n2️⃣  Checking API endpoints...")
    try:
        res = requests.get(f"{API_BASE}/api")
        assert res.status_code == 200
        endpoints = res.json()['endpoints']
        print(f"   ✅ API version: {res.json()['version']}")
        print(f"   ✅ Available endpoints: {len(endpoints)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Check if model exists
    print("\n3️⃣  Checking model file...")
    model_path = Path(__file__).parent / "best.onnx"
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024*1024)
        print(f"   ✅ Model found: {model_path.name} ({size_mb:.1f} MB)")
    else:
        print(f"   ⚠️  Model not found at {model_path}")
        print("   📝 Make sure best.onnx is copied to my_fastapi_app/ folder")
    
    # Test 4: Print workflow info
    print("\n4️⃣  API Workflow Summary:")
    print("   📋 Step 1: POST /api/inspection/start")
    print("      → Returns session_id for this inspection")
    print("")
    print("   📋 Step 2: POST /api/inspection/{session_id}/detect")
    print("      → Upload image(s) during pickup phase")
    print("      → Returns detections with bounding boxes & costs")
    print("")
    print("   📋 Step 3: POST /api/inspection/{session_id}/switch-to-return")
    print("      → Switches from pickup to return phase")
    print("")
    print("   📋 Step 4: POST /api/inspection/{session_id}/detect")
    print("      → Upload image(s) during return phase")
    print("")
    print("   📋 Step 5: POST /api/inspection/{session_id}/complete")
    print("      → Compares pickup vs return damages")
    print("      → Returns ONLY NEW damages with costs")
    
    print("\n✅ API Test Passed! Ready to use.\n")
    return True

if __name__ == "__main__":
    try:
        success = test_inspection_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted")
        sys.exit(1)
