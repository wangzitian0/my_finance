#!/usr/bin/env python3
"""Debug Ollama API calls"""

import sys

sys.path.append("dcf_engine")

import json

from ollama_client import OllamaClient


def main():
    print("🔍 Debugging Ollama API calls...")

    client = OllamaClient()
    print(f"Client config - timeout: {client.timeout}, max_tokens: {client.max_tokens}")

    # Test the exact same ping request
    print("\n1️⃣ Testing ping request...")
    result = client.generate_completion(
        prompt="Respond with exactly: 'DCF_PING_OK'", max_tokens=10, temperature=0.0
    )

    print(f"Success: {result['success']}")
    print(f"Response: '{result.get('response', 'NO_RESPONSE')}'")
    print(f"Duration: {result.get('duration_seconds', 0):.1f}s")
    if "error" in result:
        print(f"Error: {result['error']}")

    # Test with more tokens
    print("\n2️⃣ Testing with more tokens...")
    result2 = client.generate_completion(prompt="Say hello", max_tokens=50, temperature=0.0)

    print(f"Success: {result2['success']}")
    print(f"Response: '{result2.get('response', 'NO_RESPONSE')}'")
    print(f"Duration: {result2.get('duration_seconds', 0):.1f}s")


if __name__ == "__main__":
    main()
