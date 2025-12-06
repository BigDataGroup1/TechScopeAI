"""Test GPU detection and embedding model initialization."""

from src.rag.embeddings import EmbeddingModel, detect_device

print("=" * 60)
print("GPU Detection Test")
print("=" * 60)

# Test device detection
print("\n1. Testing device detection:")
print(f"   Auto-detect: {detect_device()}")
print(f"   Force CPU: {detect_device('cpu')}")
print(f"   Force CUDA: {detect_device('cuda')}")

# Test embedding model initialization
print("\n2. Testing embedding model initialization:")
try:
    print("   Initializing with auto-detect...")
    model = EmbeddingModel()
    print(f"   [OK] Model loaded successfully")
    print(f"   Device: {model.get_device()}")
    print(f"   Dimension: {model.get_dimension()}")
    
    # Test encoding
    print("\n3. Testing encoding:")
    test_texts = ["This is a test sentence.", "Another test sentence."]
    embeddings = model.encode(test_texts, batch_size=2)
    print(f"   [OK] Encoded {len(test_texts)} texts")
    print(f"   Embedding shape: {embeddings.shape}")
    
    print("\n" + "=" * 60)
    print("All tests passed! [OK]")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

