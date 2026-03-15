import sys
import os
sys.path.append(os.getcwd())
from src.resume_builder import ResumePDF

def test_v3_features():
    print("Testing Resume v3 Features...")
    
    data = {
        "name": "Sudhanshu Gochar",
        "email": "test@example.com",
        "title": "Software Engineer",
        "linkedin": "https://linkedin.com/in/test",
        "github": "https://github.com/test",
        "summary": "Experienced developer with a focus on AI and Data Science.",
        "education": {
            "college": "Indian Institute of Technology, Bombay",
            "cgpa": "9.2/10"
        },
        "github_stats": {
            "streak": 45,
            "top_language": "Python",
            "total_repos": 32,
            "joined": "2020-05-12"
        },
        "top_skills": ["Python", "TensorFlow", "React", "AWS"],
        "projects": [
            {
                "name": "AI Dashboard",
                "tech": ["Python", "Streamlit"],
                "description": ["Built a dashboard.", "Analyzed data."]
            }
        ]
    }
    
    try:
        pdf = ResumePDF()
        pdf.generate_resume(data, "test_resume_v3.pdf")
        if os.path.exists("test_resume_v3.pdf"):
            print("✅ PDF generated successfully with Education and GitHub Stats.")
        else:
            print("❌ PDF not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v3_features()
