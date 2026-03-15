
import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Conditional import for mock data (assuming it's in the same package)
try:
    from src.mock_data import get_mock_data
except ImportError:
    try:
        from mock_data import get_mock_data 
    except ImportError:
        get_mock_data = None

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
BASE_URL = "https://api.github.com"

class GitHubFetcher:
    def __init__(self, username=None, token=None):
        self.username = username or GITHUB_USERNAME
        self.token = token or GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        else:
            print("WARNING: No GitHub token provided. Rate limits will be low.")

    def _get(self, endpoint, params=None):
        url = f"{BASE_URL}/{endpoint}"
        retries = 3
        backoff = 1
        
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if reset_time:
                         wait_time = int(reset_time) - time.time() + 1
                         if wait_time > 0 and wait_time < 60: 
                             print(f"Rate limited. Waiting {wait_time:.0f}s...")
                             time.sleep(wait_time)
                             continue
                    print(f"Rate limit exceeded: {response.text}")
                    return None
                elif response.status_code >= 500:
                    print(f"Server error {response.status_code}. Retrying...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    print(f"Error fetching {url}: {response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying...")
                time.sleep(backoff)
                backoff *= 2
        return None

    def fetch_user_profile(self):
        print(f"Fetching profile for {self.username}...")
        return self._get(f"users/{self.username}")

    def fetch_repositories(self):
        print(f"Fetching repositories for {self.username}...")
        repos = []
        page = 1
        while True:
            params = {"per_page": 100, "page": page}
            data = self._get(f"users/{self.username}/repos", params=params)
            
            if data is None: 
                if page == 1: return None 
                break 
            if not data:
                break
            repos.extend(data)
            page += 1
        return repos

    def fetch_repo_files(self, repo_name):
        data = self._get(f"repos/{self.username}/{repo_name}/contents")
        files = []
        if isinstance(data, list):
            files = [item["name"] for item in data if "name" in item]
        return files

    def fetch_repo_details(self, repo_name):
        print(f"Fetching details for {repo_name}...")
        languages = self._get(f"repos/{self.username}/{repo_name}/languages")
        readme = self._get(f"repos/{self.username}/{repo_name}/readme")
        
        readme_content = ""
        if readme and "content" in readme:
            import base64
            try:
                readme_content = base64.b64decode(readme["content"]).decode("utf-8")
            except Exception as e:
                print(f"Error decoding README for {repo_name}: {e}")

        commits = self._get(f"repos/{self.username}/{repo_name}/commits", params={"per_page": 5}) 
        files = self.fetch_repo_files(repo_name)
        
        return {
            "languages": languages,
            "readme": readme_content,
            "recent_commits": commits,
            "files": files
        }

    def fetch_all_data(self, progress_callback=None):
        print(f"DEBUG: Using token: {'Yes' if self.token else 'No'}")
        
        # Try fetching profile
        profile = self.fetch_user_profile()
        
        # FALLBACK REMOVED: User requested real-time data only
        if not profile:
            print("Failed to fetch user profile (likely Rate Limit). Returning None.")
            return None
        
        repos = self.fetch_repositories()
        if repos is None:
             print("Failed to fetch repositories.")
             return None

        # LIMIT REMOVED: Fetching all repositories as requested
        # if not self.token and len(repos) > 5:
        #     print("WARNING: No token provided. Limiting to top 5 repositories.")
        #     repos = repos[:5] 

        full_data = {
            "profile": profile,
            "repositories": []
        }

        if repos:
            print(f"Found {len(repos)} repositories. Fetching details...")
            count = 0 
            total_repos = len(repos)
            for repo in repos:
                repo_name = repo["name"]
                if progress_callback:
                    progress_callback(count, total_repos, repo_name)
                
                time.sleep(0.5) 
                
                details = self.fetch_repo_details(repo_name)
                
                repo_data = {
                    "metadata": repo,
                    "details": details or {} 
                }
                full_data["repositories"].append(repo_data)
                count += 1
                if count % 5 == 0:
                     print(f"Processed {count}/{len(repos)}...")
                
        return full_data

    def save_data(self, data, filename="data/raw_data.json"):
        os.makedirs("data", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    fetcher = GitHubFetcher()
    data = fetcher.fetch_all_data()
    if data:
        fetcher.save_data(data)
