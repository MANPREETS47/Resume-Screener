import socket
import ssl

PROVIDERS = [
    ("api.groq.com", 443),
    ("api.openai.com", 443),
    ("api.anthropic.com", 443),
    ("openrouter.ai", 443)
]

def check_ssl(hostname, port):
    print(f"\nTesting SSL to {hostname}:{port}...", end=" ")
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"OK ({ssock.version()})")
                return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Checking LLM Provider Connectivity:")
    results = {}
    for host, port in PROVIDERS:
        results[host] = check_ssl(host, port)
    
    print("\nSummary:")
    for host, status in results.items():
        print(f"{host}: {'Accessible' if status else 'Blocked'}")
