#!/usr/bin/env python3
"""
Temporary fix for torch compatibility issues with Graph RAG system.
This script patches the missing torch.uint64 attribute that's causing import errors.
"""

import sys

import torch

# Patch missing torch.uint64 if not available
if not hasattr(torch, "uint64"):
    print("Patching torch.uint64 compatibility issue...")
    torch.uint64 = torch.int64
    print("✅ Torch compatibility patch applied")

# Test basic functionality
try:
    print("Testing basic Graph RAG imports...")

    # Test sentence transformers import
    from sentence_transformers import SentenceTransformer

    print("✅ sentence_transformers import successful")

    # Test basic graph_rag imports
    from graph_rag.data_loader import DataLoader

    print("✅ graph_rag.data_loader import successful")

    from graph_rag.graph_database import GraphDatabase

    print("✅ graph_rag.graph_database import successful")

    print("\n🎉 Basic Graph RAG compatibility test passed!")
    print("Graph RAG system should now work correctly.")

except Exception as e:
    print(f"❌ Compatibility test failed: {e}")
    sys.exit(1)
