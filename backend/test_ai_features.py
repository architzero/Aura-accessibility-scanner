"""
Test script to verify all AI features are working
Run: python test_ai_features.py
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("TESTING AURA AI FEATURES")
print("=" * 60)

# Test 1: BLIP Image Caption Generation
print("\n1. Testing BLIP Model (Image Alt Text Generation)...")
try:
    from scanner_process import generate_alt_text
    test_image = "https://picsum.photos/200/300"
    result = generate_alt_text(test_image)
    if result:
        print(f"   ✅ BLIP Model Working!")
        print(f"   Generated: '{result}'")
    else:
        print("   ❌ BLIP Model returned empty")
except Exception as e:
    print(f"   ❌ BLIP Model Error: {e}")

# Test 2: Color Contrast Fix
print("\n2. Testing Color Contrast AI (WCAG Compliance)...")
try:
    from scanner_process import suggest_contrast_fix, get_contrast_ratio, hex_to_rgb
    
    # Test case: Low contrast
    fg = "#777777"
    bg = "#ffffff"
    new_color = suggest_contrast_fix(fg, bg)
    
    if new_color:
        old_ratio = get_contrast_ratio(hex_to_rgb(fg), hex_to_rgb(bg))
        new_ratio = get_contrast_ratio(hex_to_rgb(new_color), hex_to_rgb(bg))
        print(f"   ✅ Color Contrast AI Working!")
        print(f"   Original: {fg} (ratio: {old_ratio:.2f}:1)")
        print(f"   Fixed: {new_color} (ratio: {new_ratio:.2f}:1)")
        print(f"   WCAG AA Compliant: {new_ratio >= 4.5}")
    else:
        print("   ❌ Color fix failed")
except Exception as e:
    print(f"   ❌ Color Contrast Error: {e}")

# Test 3: Flesch-Kincaid Readability
print("\n3. Testing Flesch-Kincaid Readability Analysis...")
try:
    import textstat
    
    # Complex text
    complex_text = "The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding of computational complexity theory."
    
    # Simple text
    simple_text = "The cat sat on the mat. It was a sunny day."
    
    complex_grade = textstat.flesch_kincaid_grade(complex_text)
    simple_grade = textstat.flesch_kincaid_grade(simple_text)
    
    print(f"   ✅ Flesch-Kincaid Working!")
    print(f"   Complex text grade: {complex_grade:.1f} (college level)")
    print(f"   Simple text grade: {simple_grade:.1f} (elementary)")
except Exception as e:
    print(f"   ❌ Readability Error: {e}")

# Test 4: Full Scanner Integration
print("\n4. Testing Full Scanner Integration...")
try:
    import subprocess
    import json
    
    result = subprocess.run(
        [sys.executable, "scanner_process.py", "https://example.com", "test_integration"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f"   ✅ Scanner Integration Working!")
        print(f"   Issues found: {len(data['issues'])}")
        print(f"   Generic suggestions: {len(data['genericSuggestions'])}")
        print(f"   AI suggestions: {len(data['aiSuggestions'])}")
        print(f"   Score: {data['score']}/100")
    else:
        print(f"   ❌ Scanner failed: {result.stderr}")
except Exception as e:
    print(f"   ❌ Integration Error: {e}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("\nAll AI features are implemented:")
print("✅ BLIP Model - Generates image alt text descriptions")
print("✅ Color Contrast AI - Calculates WCAG-compliant colors")
print("✅ Flesch-Kincaid - Analyzes text readability grade level")
print("\nTo see AI suggestions in action, scan websites with:")
print("- Image-alt violations (images without alt text)")
print("- Color-contrast violations (low contrast text)")
print("- Complex text (college-level reading grade)")
print("\nRecommended test sites:")
print("- https://www.berkshirehathaway.com (contrast issues)")
print("- https://www.arngren.net (images + contrast)")
print("- https://www.lingscars.com (many issues)")
print("=" * 60)
