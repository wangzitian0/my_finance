#!/usr/bin/env python3

print("🔍 [DEBUG] Starting test script")

import argparse

print("🔍 [DEBUG] argparse imported")

import json

print("🔍 [DEBUG] json imported")

import subprocess

print("🔍 [DEBUG] subprocess imported")

import sys

print("🔍 [DEBUG] sys imported")

import time

print("🔍 [DEBUG] time imported")

from datetime import datetime

print("🔍 [DEBUG] datetime imported")

from pathlib import Path

print("🔍 [DEBUG] pathlib imported")

print("🔍 [DEBUG] All imports completed")

# Test constants
BUILD_DATA = "build_data"
print("🔍 [DEBUG] Constants defined")


def main():
    print("🔍 [DEBUG] Main function called")
    parser = argparse.ArgumentParser(description="Test script")
    parser.add_argument("title", help="Test title")
    parser.add_argument("issue", type=int, help="Test issue")

    print("🔍 [DEBUG] About to parse args")
    args = parser.parse_args()
    print(f"🔍 [DEBUG] Args parsed: {args}")

    print("🔍 [DEBUG] Test completed successfully")


if __name__ == "__main__":
    print("🔍 [DEBUG] __main__ block entered")
    main()