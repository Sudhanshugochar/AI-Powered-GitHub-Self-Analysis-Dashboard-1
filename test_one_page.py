import sys
import os
sys.path.append(os.getcwd())
try:
    from src.resume_builder import ResumePDF
    print("✅ src.resume_builder imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_one_page_layout():
    print("Testing One-Page Layout with 6 Projects...")
    
    data = {
        "name": "Sudhanshu Gochar",
        "email": "test@example.com",
        "title": "Software Engineer",
        "linkedin": "https://linkedin.com/in/test",
        "github": "https://github.com/test",
        "summary": "Highly motivated engineer with a passion for AI. " * 3, # 3 lines
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
        "top_skills": ["Python", "TensorFlow", "React", "AWS", "Docker", "Kubernetes", "CI/CD"],
        "projects": [
            {
                "name": f"Project {i}",
                "tech": ["Python", "AI"],
                "description": ["Built a thing.", "Optimized it bye 50%."]
            } for i in range(1, 9) # 8 projects
        ]
    }
    
    try:
        pdf = ResumePDF()
        pdf.generate_resume(data, "test_resume_one_page.pdf")
        if os.path.exists("test_resume_one_page.pdf"):
            print("✅ PDF generated. Please check if it fits on one page.")
        else:
            print("❌ PDF not found.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_one_page_layout()
