import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.llm_analysis import OllamaAnalyzer

def test_multilingual_analysis():
    print("Testing OllamaAnalyzer with target_language='Spanish'...")
    
    analyzer = OllamaAnalyzer(target_language="Spanish")
    
    # Test 1: Sentiment Analysis
    print("\n--- Testing Sentiment Analysis (Expected: Spanish) ---")
    text = "I love this project! It's amazing."
    try:
        sentiment = analyzer.analyze_sentiment(text)
        print(f"Input: {text}")
        print(f"Output: {sentiment}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Topic Classification
    print("\n--- Testing Topic Classification (Expected: Spanish) ---")
    desc = "A repository for building machine learning models using Python."
    try:
        topic = analyzer.classify_topic(desc)
        print(f"Input: {desc}")
        print(f"Output: {topic}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_multilingual_analysis()
