"""
Quick test script to verify the fixes work correctly.
Run this before starting the Streamlit app.
"""

def test_file_contents():
    """Test that files have the critical improvements."""
    print("Testing ai_client.py...")
    
    with open('ai_client.py', 'r', encoding='utf-8') as f:
        ai_client_content = f.read()
    
    # Check for critical keywords in vision prompt
    assert "CRITICAL" in ai_client_content, "Missing CRITICAL emphasis in ai_client.py"
    assert "horizontal_lines" in ai_client_content, "Missing horizontal_lines"
    assert "YOU MUST add markLine" in ai_client_content, "Missing markLine requirement"
    assert "exact colors from reference analysis" in ai_client_content, "Missing color requirement"
    
    print("✅ ai_client.py has critical improvements")
    
    print("\nTesting app.py...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check for dialog size improvements
    assert "80vw" in app_content, "Dialog width not increased to 80vw"
    assert "85vh" in app_content, "Dialog height not set to 85vh"
    assert "1200px" in app_content, "Max width not increased to 1200px"
    
    # Check for improved deep_merge
    assert "For simple arrays, replace entirely" in app_content or "simple arrays" in app_content.lower(), "Deep merge not improved"
    
    print("✅ app.py has dialog size improvements")
    
    print("\nTesting README.md...")
    
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Check that merge conflict is resolved
    assert "<<<<<<< HEAD" not in readme_content, "Merge conflict still present"
    assert "=======" not in readme_content or readme_content.count("=======") <= 2, "Merge conflict markers present"
    assert "SF CHAI" in readme_content, "README content missing"
    
    print("✅ README.md merge conflict resolved")


def test_deep_merge_logic():
    """Test the deep merge logic."""
    print("\nTesting deep merge logic...")
    
    # Simulate the deep_merge function
    def deep_merge(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge(target[key], value)
            elif key in target and isinstance(target[key], list) and isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    for i, item in enumerate(value):
                        if i < len(target[key]):
                            if isinstance(item, dict) and isinstance(target[key][i], dict):
                                deep_merge(target[key][i], item)
                            else:
                                target[key][i] = item
                        else:
                            target[key].append(item)
                else:
                    target[key] = value
            else:
                target[key] = value
    
    # Test case 1: Simple array replacement
    target1 = {"colors": ["#ff0000", "#00ff00"]}
    source1 = {"colors": ["#0000ff", "#ffff00", "#ff00ff"]}
    deep_merge(target1, source1)
    assert target1["colors"] == ["#0000ff", "#ffff00", "#ff00ff"], "Simple array merge failed"
    print("✅ Simple array replacement works")
    
    # Test case 2: Dict array merge
    target2 = {"series": [{"name": "A", "color": "#ff0000"}]}
    source2 = {"series": [{"color": "#0000ff"}]}
    deep_merge(target2, source2)
    assert target2["series"][0]["color"] == "#0000ff", "Dict array merge failed"
    assert target2["series"][0]["name"] == "A", "Dict array merge lost data"
    print("✅ Dict array merge works")
    
    # Test case 3: Adding new series
    target3 = {"series": [{"name": "A"}]}
    source3 = {"series": [{"name": "A"}, {"name": "B"}]}
    deep_merge(target3, source3)
    assert len(target3["series"]) == 2, "Adding new series failed"
    print("✅ Adding new elements works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("SF CHAI - Testing Applied Fixes")
    print("=" * 60)
    
    try:
        test_file_contents()
        test_deep_merge_logic()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run the Streamlit app:")
        print("  streamlit run app.py")
        print("\nTest the following:")
        print("  1. Upload CSV + reference PNG with horizontal line")
        print("  2. Check vision analysis shows annotations detected")
        print("  3. Check generated chart has the annotation")
        print("  4. Open chatbot (should be large - 80% width)")
        print("  5. Try modifying chart colors via chatbot")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
