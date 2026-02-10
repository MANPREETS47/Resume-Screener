import asyncio
import os
import httpx
import socket
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
HOST = "api.groq.com"
PORT = 443

print(f"Python: {sys.version.split()[0]}")
print(f"HTTPX: {httpx.__version__}")
print(f"API Key: {API_KEY[:5]}..." if API_KEY else "API Key: None")

def test_socket():
    print(f"\nTesting TCP connection to {HOST}:{PORT}...")
    try:
        # Resolve IP first
        ip = socket.gethostbyname(HOST)
        print(f"Resolved {HOST} to {ip}")
        
        # Connect
        sock = socket.create_connection((HOST, PORT), timeout=10)
        print("TCP Connection successful!")
        sock.close()
        return True
    except Exception as e:
        print(f"TCP Connection failed: {type(e).__name__}: {e}")
        return False

async def test_https():
    print(f"\nTesting HTTPS POST to {BASE_URL}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(BASE_URL, json=payload, headers=headers)
            print(f"HTTP Status: {response.status_code}")
            if response.status_code == 200:
                print("Response content:", response.text[:200])
            else:
                print("Error response:", response.text)
    except Exception as e:
        print(f"\nHTTPX Exception: {repr(e)}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"Cause: {repr(e.__cause__)}")
            
if __name__ == "__main__":
    if test_socket():
        asyncio.run(test_https())
    else:
        print("Skipping HTTPS test due to TCP failure.")
