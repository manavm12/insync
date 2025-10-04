"""
Simple Text Correction using OpenAI API

This module takes incomplete or broken sentences and corrects them into proper English.
"""

from openai import OpenAI
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def fix_sentence(broken_text: str, api_key: Optional[str] = None) -> str:
    """
    Fix incomplete or broken sentences using OpenAI.
    
    Args:
        broken_text: Incomplete sentence like "i write pen"
        api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var)
        
    Returns:
        Fixed sentence like "I write with a pen"
    """
    # Get API key
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable."
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    if not broken_text or broken_text.strip() == "":
        return "No text to translate"
    
    # System prompt for text correction
    system_prompt = """You are a text correction assistant. Fix incomplete or broken sentences into proper English.

Rules:
1. Correct grammar and add missing words (articles, prepositions, etc.)
2. Capitalize properly
3. Keep the original meaning
4. Make it sound natural
5. Keep it simple and concise

Examples:
Input: "i write pen"
Output: "I write with a pen"

Input: "she go store buy milk"
Output: "She goes to the store to buy milk"

Input: "we eat food good"
Output: "We eat good food"

Fix the following text:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": broken_text}
            ],
            max_tokens=100,
            temperature=0.3,  # Lower temperature for more consistent corrections
        )
        
        fixed_text = response.choices[0].message.content.strip()
        return fixed_text
        
    except Exception as e:
        error_message = str(e)
        if "rate_limit" in error_message.lower():
            return "Rate limit exceeded. Please try again later."
        elif "authentication" in error_message.lower() or "api_key" in error_message.lower():
            return "Authentication error. Please check your API key."
        elif "api" in error_message.lower():
            return f"API error: {error_message}"
        else:
            return f"Translation error: {error_message}"


# Example usage and testing
if __name__ == "__main__":
    # Test the translator (requires OPENAI_API_KEY environment variable)
    test_sentences = [
        "i write pen",
        "she go store",
        "we eat food good",
        "he run fast car",
        "they play music loud",
        "cat sit table",
        "book read interesting"
    ]
    
    print("🤖 Testing Text Correction")
    print("=" * 40)
    
    for sentence in test_sentences:
        try:
            result = fix_sentence(sentence)
            print(f"Input:  {sentence}")
            print(f"Output: {result}")
            print("-" * 40)
        except Exception as e:
            print(f"Error testing sentence '{sentence}': {e}")
            print("-" * 40)
