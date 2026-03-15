import sys
import os
sys.path.append(os.getcwd())
import json

from src.llm_analysis import OllamaAnalyzer
from src.resume_builder import ResumePDF

def test_resume_generation():
    print("Testing Resume Generation...")
    
    # 1. Test LLM Generation (Mocking data for speed/cost if needed, but let's try real first)
    analyzer = OllamaAnalyzer()
    
    user_profile = "Name: Test User, Bio: Python Developer, Repos: 10, Top Lang: Python"
    repo_summaries = "- Repo1: Data Science Tool (Python)\n- Repo2: Web App (Streamlit)"
    
    print("Generating content from LLM...")
    json_content = analyzer.generate_resume_content(user_profile, repo_summaries)
    
    if not json_content:
        print("❌ LLM failed to return content.")
        return
        
    print(f"LLM Response: {json_content[:100]}...")
    
    try:
        data = json.loads(json_content)
        # Fill missing fields
        data['name'] = "Test User"
        data['email'] = "test@example.com"
        
        # 2. Test PDF Generation
        print("Generating PDF...")
        pdf = ResumePDF()
        pdf.generate_resume(data, "test_resume.pdf")
        
        if os.path.exists("test_resume.pdf"):
            print("✅ PDF generated successfully: test_resume.pdf")
        else:
            print("❌ PDF generation failed.")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Raw Content: {json_content}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_resume_generation()
