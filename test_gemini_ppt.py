"""Quick test script to generate a PowerPoint using Gemini."""

import os
from dotenv import load_dotenv
load_dotenv()

from src.utils.exporters import PitchExporter
from src.utils.gemini_enhancer import GeminiSlideEnhancer

# Sample slides for testing
test_slides = [
    {
        "slide_number": 1,
        "title": "Our Company",
        "content": "We are a tech startup solving problems",
        "key_points": ["Innovative solution", "Great team", "Big market"]
    },
    {
        "slide_number": 2,
        "title": "The Problem",
        "content": "Current solutions are inefficient",
        "key_points": ["High costs", "Slow processes", "Poor user experience"]
    },
    {
        "slide_number": 3,
        "title": "Our Solution",
        "content": "We provide an AI-powered platform",
        "key_points": ["Fast", "Cost-effective", "User-friendly"]
    }
]

print("🧪 Testing Gemini PowerPoint Generation...")
print("=" * 60)

# Test Gemini enhancer
print("\n1️⃣ Testing Gemini Enhancer...")
enhancer = GeminiSlideEnhancer()
if enhancer.enabled:
    print("✅ Gemini enhancer is ready!")
    
    # Test full rewrite
    print("\n2️⃣ Testing full deck rewrite with Gemini...")
    try:
        rewritten = enhancer.rewrite_full_pitch_deck(
            test_slides,
            "Test Company",
            {"annual_revenue": "$500K", "growth_rate": "20% MoM"}
        )
        print(f"✅ Rewritten {len(rewritten)} slides")
        print(f"   First slide title: {rewritten[0].get('title')}")
        print(f"   Enhanced by: {rewritten[0].get('enhanced_by', 'unknown')}")
    except Exception as e:
        print(f"❌ Rewrite failed: {e}")
else:
    print("❌ Gemini not enabled - check API key")

# Test PowerPoint generation
print("\n3️⃣ Testing PowerPoint generation with Gemini...")
exporter = PitchExporter()
try:
    pptx_path = exporter.export_to_powerpoint(
        test_slides,
        "Test Company",
        include_images=False,  # Skip images for quick test
        enhance_with_ai=True,
        company_data={"annual_revenue": "$500K"},
        full_rewrite=True,
        ai_provider="gemini"  # Force Gemini
    )
    if pptx_path:
        print(f"✅ PowerPoint created: {pptx_path}")
        print("✅ SUCCESS! Gemini PowerPoint generation works!")
    else:
        print("❌ PowerPoint generation returned None")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 Test complete!")

