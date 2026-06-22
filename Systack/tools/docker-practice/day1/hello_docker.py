#!/usr/bin/env python3
from datetime import datetime

def main():
    print("=" * 50)
    print("Hello from inside a Docker container!")
    print("=" * 50)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Python version: 3.11 (running in a container)")
    print()
    print("If you're seeing this, your Dockerfile works!")
    print("=" * 50)

if __name__ == "__main__":
    main()
