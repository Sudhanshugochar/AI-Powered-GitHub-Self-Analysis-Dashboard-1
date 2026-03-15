
import random
from datetime import datetime

def get_mock_data(username="Demo User"):
    # Current timestamp
    now = datetime.now().isoformat()
    
    # Dynamic Profile based on username
    profile = {
        "login": username,
        "id": random.randint(10000, 99999),
        "avatar_url": f"https://github.com/{username}.png", # GitHub often redirects this to a default if not found
        "html_url": f"https://github.com/{username}",
        "name": username.replace("-", " ").title(),
        "company": "Tech Corp",
        "blog": f"https://{username.lower()}.dev",
        "location": "San Francisco, CA",
        "email": f"{username.lower()}@example.com",
        "bio": "Full Stack Developer | AI Enthusiast | Open Source Contributor",
        "public_repos": 25,
        "followers": 150,
        "following": 50,
        "created_at": "2020-01-01T12:00:00Z",
        "updated_at": now
    }

    # Dynamic Repos
    repo_names = [
        "ai-dashboard", 
        "react-native-starter", 
        "go-microservices", 
        "data-pipeline-airflow", 
        "algo-trading-bot",
        "portfolio-v2",
        "machine-learning-101",
        "django-ecommerce"
    ]
    
    repos_data = []
    for name in repo_names:
        repo_full_name = f"{username}/{name}"
        repo = {
            "name": name,
            "full_name": repo_full_name,
            "description": f"A sample project for {name.replace('-', ' ')}.",
            "stargazers_count": random.randint(10, 500),
            "forks_count": random.randint(5, 100),
            "language": random.choice(["Python", "JavaScript", "Go", "TypeScript", "Jupyter Notebook"]),
            "size": random.randint(1000, 10000),
            "created_at": "2021-01-01T12:00:00Z",
            "updated_at": now,
            "topics": ["demo", "project", "opensource"],
            "html_url": f"https://github.com/{repo_full_name}" 
        }
        
        # Simulate details
        details = {
            "languages": {repo["language"]: 10000, "HTML": 2000, "CSS": 1000},
            "readme": f"# {name}\n\n{repo['description']}\n\n## Features\n- Feature A\n- Feature B\n\n## Installation\n\n```bash\nnpm install\n```",
            "recent_commits": [
                {
                    "commit": {
                        "message": f"Update README for {name}",
                        "author": {"name": username, "date": now}
                    }
                },
                {
                    "commit": {
                        "message": "Bug fix in core logic",
                        "author": {"name": username, "date": now}
                    }
                }
            ],
            "files": ["README.md", "package.json", ".gitignore", "src/", "tests/"]
        }
        
        repos_data.append({
            "metadata": repo,
            "details": details
        })
        
    return {
        "profile": profile,
        "repositories": repos_data
    }
