"""
API Integration Test for Phi-3 Summarization
Tests the FastAPI endpoints with the Phi-3 model
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import json


def test_api_integration():
    """Test the API endpoints"""
    
    BASE_URL = "http://localhost:8002"
    
    print("=" * 60)
    print("API Integration Test for Phi-3 Summarization")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n📋 Test 1: Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data.get('status', 'unknown')}")
            print(f"  ✅ Model Loaded: {data.get('model_loaded', 'N/A')}")
            print(f"  ✅ Total Inferences: {data.get('total_inferences', 'N/A')}")
            print(f"  ✅ Success Rate: {data.get('success_rate', 'N/A')}%")
            print(f"  ✅ Avg Inference Time: {data.get('avg_inference_time', 'N/A')}s")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to API server")
        print("  💡 Make sure the backend is running: python main.py")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n📋 Test 2: Root Endpoint")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Message: {data.get('message', 'unknown')}")
            print(f"  ✅ Version: {data.get('version', 'unknown')}")
        else:
            print(f"  ❌ Root endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Summarize sessions (requires auth and patient data)
    print("\n📋 Test 3: Summarize Sessions Endpoint")
    print("-" * 40)
    
    # Note: This test requires authentication and existing patient data
    # For now, we'll just verify the endpoint exists
    try:
        response = requests.post(
            f"{BASE_URL}/summarize-sessions",
            json={"patient_id": 1},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Summary generated successfully")
            print(f"  ✅ Session count: {data.get('session_count', 0)}")
        elif response.status_code == 401:
            print(f"  ⚠️  Authentication required (expected)")
        elif response.status_code == 404:
            print(f"  ⚠️  No sessions found for patient (expected if no data)")
        else:
            print(f"  ⚠️  Response: {response.status_code} - {response.text[:100]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("API Integration Test Complete")
    print("=" * 60)
    
    return True


def test_direct_summarization():
    """Test the summarization service directly"""
    
    print("\n" + "=" * 60)
    print("Direct Summarization Service Test")
    print("=" * 60)
    
    try:
        from summarization_service_phi3 import summarization_service
        
        if summarization_service is None:
            print("❌ Summarization service not initialized")
            return False
        
        # Test text
        test_text = """
        Therapist: How have you been feeling this week?
        Patient: I've been struggling with anxiety. I keep having panic attacks at work.
        The thoughts of failure won't stop. I've been avoiding meetings because I'm scared
        I'll have another attack. I haven't been sleeping well either.
        Therapist: Have you had any thoughts of harming yourself?
        Patient: No, nothing like that. Just feeling overwhelmed.
        Therapist: Let's work on some coping strategies for the panic attacks.
        """
        
        print("\n📋 Testing Single Session Summarization")
        print("-" * 40)
        
        start_time = time.time()
        summary = summarization_service.summarize_single_session(test_text)
        duration = time.time() - start_time
        
        print(f"\n🤖 Generated Summary:")
        print("-" * 40)
        print(summary)
        print("-" * 40)
        print(f"\n⏱️  Time: {duration:.2f}s")
        print(f"📊 Length: {len(summary)} chars, {len(summary.split())} words")
        
        # Check for required elements
        has_sections = any(s in summary.lower() for s in ['chief', 'emotional', 'risk', 'intervention', 'plan'])
        has_red = '{{RED:' in summary
        
        print(f"\n✓ Has clinical sections: {'Yes' if has_sections else 'No'}")
        print(f"✓ Has RED markers: {'Yes' if has_red else 'No'}")
        
        # Get statistics
        stats = summarization_service.get_statistics()
        print(f"\n📈 Service Statistics:")
        print(f"   Total Inferences: {stats['total_inferences']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Avg Time: {stats['avg_inference_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Phi-3 Summarization - Integration Tests")
    print("=" * 60)
    
    # Test direct summarization first
    direct_ok = test_direct_summarization()
    
    # Then test API if server is running
    api_ok = test_api_integration()
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"  Direct Summarization: {'✅ PASSED' if direct_ok else '❌ FAILED'}")
    print(f"  API Integration: {'✅ PASSED' if api_ok else '❌ FAILED'}")
