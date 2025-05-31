import os
import socket
import sys

def check_port(port=8000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        sock.close()
        return True
    except OSError:
        return False

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Checking port {port} availability...")
    if not check_port(port):
        print(f"❌ ERROR: Port {port} is already in use")
        sys.exit(1)
    print(f"✅ Port {port} is available")
    print(f"Environment variables: {os.environ}")
    sys.exit(0)
