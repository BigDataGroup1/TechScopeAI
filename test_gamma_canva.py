"""
Quick test script for Gamma.ai and Canva integrations.
Tests with minimal slides (3 slides) to verify functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.gamma_integration import GammaIntegration
from src.utils.canva_integration import CanvaIntegration


def test_integrations():
    """Test Gamma.ai and Canva integrations with minimal slides."""
    
    print("🧪 Testing Gamma.ai and Canva Integrations\n")
    print("=" * 60)
    
    # Create minimal test slides (just 3 slides)
    test_slides = [
        {
            "slide_number": 1,
            "title": "Test Company",
            "content": "This is a test pitch deck to verify Gamma.ai and Canva integrations.",
            "key_points": ["Test point 1", "Test point 2"]
        },
        {
            "slide_number": 2,
            "title": "Problem",
            "content": "We are solving a test problem for demonstration purposes.",
            "key_points": ["Problem 1", "Problem 2"]
        },
        {
            "slide_number": 3,
            "title": "Solution",
            "content": "Our solution addresses the test problem effectively.",
            "key_points": ["Solution 1", "Solution 2"]
        }
    ]
    
    company_name = "Test Company"
    
    # Test Gamma.ai
    print("\n🤖 Testing Gamma.ai Integration...")
    print("-" * 60)
    try:
        gamma = GammaIntegration()
        themes = gamma.get_available_themes()
        print(f"✅ Found {len(themes)} Gamma.ai themes:")
        for theme in themes:
            print(f"   - {theme['name']}: {theme['description']}")
        
        print(f"\n📝 Creating Gamma.ai presentation with theme: {themes[0]['id']}...")
        gamma_result = gamma.create_presentation(
            test_slides,
            company_name,
            theme_id=themes[0]['id'],
            enhance_with_ai=True
        )
        
        if gamma_result.get('success'):
            print("✅ Gamma.ai presentation created successfully!")
            print(f"   Presentation ID: {gamma_result.get('presentation_id')}")
            print(f"   View URL: {gamma_result.get('presentation_url')}")
            print(f"   Edit URL: {gamma_result.get('edit_url')}")
            print(f"   Theme: {gamma_result.get('theme')}")
            print(f"   AI Enhanced: {gamma_result.get('ai_enhanced')}")
        else:
            print(f"❌ Gamma.ai creation failed: {gamma_result.get('error')}")
            print(f"   Message: {gamma_result.get('message')}")
    except Exception as e:
        print(f"❌ Gamma.ai test error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Canva
    print("\n\n🎨 Testing Canva Integration...")
    print("-" * 60)
    try:
        canva = CanvaIntegration()
        templates = canva.get_available_templates()
        print(f"✅ Found {len(templates)} Canva templates:")
        for template in templates:
            print(f"   - {template['name']}: {template['description']}")
        
        print(f"\n📝 Creating Canva presentation with template: {templates[0]['id']}...")
        canva_result = canva.create_presentation(
            test_slides,
            company_name,
            template_id=templates[0]['id'],
            enhance_visuals=True
        )
        
        if canva_result.get('success'):
            print("✅ Canva presentation created successfully!")
            print(f"   Design ID: {canva_result.get('design_id')}")
            print(f"   View URL: {canva_result.get('design_url')}")
            print(f"   Edit URL: {canva_result.get('edit_url')}")
            print(f"   Template: {canva_result.get('template')}")
            print(f"   Visual Enhanced: {canva_result.get('visual_enhanced')}")
        else:
            print(f"❌ Canva creation failed: {canva_result.get('error')}")
            print(f"   Message: {canva_result.get('message')}")
    except Exception as e:
        print(f"❌ Canva test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("\n📋 Summary:")
    print("   - This test uses placeholder implementations")
    print("   - To use real APIs, update _create_via_api() methods")
    print("   - Add GAMMA_API_KEY and CANVA_API_KEY to .env file")
    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_integrations()

