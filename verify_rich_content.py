import sys
import os
sys.path.append(os.getcwd())
try:
    from src.llm_analysis import OllamaAnalyzer
    print("✅ src.llm_analysis imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_rich_content():
    print("Testing Rich Content Generation...")
    analyzer = OllamaAnalyzer()
    
    # Mock profile data
    user_profile = "Name: Developer X, Bio: Full Stack, Repos: 20, Top Lang: Python"
    repo_summaries = "- Repo A: Complex AI Dashboard\n- Repo B: E-commerce Platform"
    
    # Generate
    content = analyzer.generate_resume_content(user_profile, repo_summaries)
    
    if content:
        print("✅ Content extracted.")
        print(f"Snippet: {content[:100]}...")
        if "Architected" in content or "Reduced" in content or "optimized" in content:
             print("✅ Content seems impactful (contains action verbs).")
        else:
             print("⚠️ Content might still be generic.")
    else:
        print("❌ Failed to generate content.")

if __name__ == "__main__":
    test_rich_content()
