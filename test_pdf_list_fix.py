import sys
import os
sys.path.append(os.getcwd())
from src.resume_builder import ResumePDF

def test_list_handling():
    print("Testing PDF Generation with Lists...")
    
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "summary": "Summary",
        "top_skills": ["Python", "Java"], # List
        "projects": [
            {
                "name": "Project 1",
                "tech": ["Python", "Streamlit"], # List
                "description": ["Bullet 1", "Bullet 2"] # List
            }
        ]
    }
    
    try:
        pdf = ResumePDF()
        pdf.generate_resume(data, "test_list_fix.pdf")
        if os.path.exists("test_list_fix.pdf"):
            print("✅ PDF generated successfully with list inputs.")
        else:
            print("❌ PDF not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_handling()
