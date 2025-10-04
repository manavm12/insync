#!/usr/bin/env python3
"""
Test script for text correction using OpenAI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks.gesture_translator import fix_sentence


def test_text_correction():
    """Test the text correction function."""
    print("🤖 Testing Text Correction with OpenAI")
    print("=" * 50)
    print("Make sure you have OPENAI_API_KEY set in your environment")
    print("=" * 50)
    
    # Test sentences
    test_cases = [
        "i write pen",
        "she go store buy milk", 
        "we eat food good",
        "he run fast car",
        "they play music loud",
        "cat sit table",
        "book read interesting",
        "me want water drink",
        "you come here now"
    ]
    
    for i, broken_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{broken_text}'")
        
        try:
            fixed_text = fix_sentence(broken_text)
            print(f"   Result: '{fixed_text}'")
            
            if "Error:" in fixed_text:
                print("   ❌ Error occurred")
            else:
                print("   ✅ Success")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Interactive Test - Enter your own broken sentences:")
    print("(Type 'quit' to exit)")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nEnter broken text: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not user_input:
                continue
                
            print("Fixing...")
            result = fix_sentence(user_input)
            print(f"Fixed: '{result}'")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    test_text_correction()
