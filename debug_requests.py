import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")

def test_groq_requests(verify_ssl=True):
    print(f"\n--- Testing with SSL Verify={verify_ssl} ---")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "ping"}]
    }
    
    try:
        response = requests.post(
            URL, 
            headers=headers, 
            json=data, 
            timeout=10,
            verify=verify_ssl
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print(f"API Key present: {bool(API_KEY)}")
    print(f"Target URL: {URL}")
    
    # 1. Normal test
    print("\n1. Standard Request:")
    success = test_groq_requests(verify_ssl=True)
    
    # 2. No SSL test (only if 1 fails)
    if not success:
        print("\n2. Request WITHOUT SSL Verification (Insecure):")
        test_groq_requests(verify_ssl=False)
