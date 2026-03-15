import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os

try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except Exception as e:
    print(f"Warning: scikit-learn/numpy not available ({e})")
    SKLEARN_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception as e:
    print(f"Warning: prophet not available ({e})")
    PROPHET_AVAILABLE = False

class TraditionalAnalyzer:
    def __init__(self, data_path="data/raw_data.json"):
        self.data_path = data_path
        self.repos_df = None
        self.commits_df = None
        self.profile_data = {}

    def load_data(self):
        if not os.path.exists(self.data_path):
            print(f"Data file not found at {self.data_path}")
            return False

        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.profile_data = data.get("profile", {})
        repos = data.get("repositories", [])

        # Process Repositories
        repo_list = []
        all_commits = []

        for item in repos:
            repo_meta = item.get("metadata", {})
            repo_details = item.get("details", {})
            
            repo_list.append({
                "name": repo_meta.get("name"),
                "description": repo_meta.get("description", ""),
                "stars": repo_meta.get("stargazers_count", 0),
                "forks": repo_meta.get("forks_count", 0),
                "language": repo_meta.get("language", "Unknown"),
                "size": repo_meta.get("size", 0),
                "created_at": pd.to_datetime(repo_meta.get("created_at"), errors='coerce'),
                "updated_at": pd.to_datetime(repo_meta.get("updated_at"), errors='coerce'),
                "topics": repo_meta.get("topics", []),
                "readme_length": len(repo_details.get("readme", "")),
                "readme_content": repo_details.get("readme", ""),
                "files": repo_details.get("files", [])
            })

            # Process Commits
            commits = repo_details.get("recent_commits", [])
            if commits:
                for commit in commits:
                    c_meta = commit.get("commit", {})
                    author_date = c_meta.get("author", {}).get("date")
                    if author_date:
                        all_commits.append({
                            "repo_name": repo_meta.get("name"),
                            "date": pd.to_datetime(author_date),
                            "message": c_meta.get("message"),
                            "author": c_meta.get("author", {}).get("name")
                        })

        self.repos_df = pd.DataFrame(repo_list)
        self.commits_df = pd.DataFrame(all_commits)
        print("Data loaded successfully.")
        return True

    def get_basic_stats(self):
        if self.repos_df is None: return {}
        return {
            "total_repos": len(self.repos_df),
            "total_stars": self.repos_df['stars'].sum(),
            "top_languages": self.repos_df['language'].value_counts().to_dict(),
            "total_commits_tracked": len(self.commits_df) if self.commits_df is not None else 0
        }

    def perform_clustering(self, n_clusters=3):
        if not SKLEARN_AVAILABLE:
            print("Clustering disabled: scikit-learn is not available.")
            return None
        if self.repos_df is None or self.repos_df.empty:
            return None
        
        # Features for clustering: stars, forks, size, readme_length
        features = self.repos_df[['stars', 'forks', 'size', 'readme_length']].fillna(0)
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        self.repos_df['cluster'] = clusters
        return self.repos_df[['name', 'cluster', 'stars', 'forks']]

    def get_user_stats(self):
        """Calculates advanced user statistics for GitHub Replay."""
        stats = {
            "top_language": "Unknown",
            "longest_streak": 0,
            "most_productive_day": "Unknown",
            "total_commits": 0,
            "chronotype": "Day Walker",
            "most_active_month": "Unknown"
        }

        if self.repos_df is not None and not self.repos_df.empty:
            lang_counts = self.repos_df['language'].value_counts()
            if not lang_counts.empty:
                stats["top_language"] = lang_counts.idxmax()

        if self.commits_df is not None and not self.commits_df.empty:
            # 0. Total Commits
            stats["total_commits"] = len(self.commits_df)

            # 1. Longest Streak
            # Group by date to get unique days with commits
            dates = self.commits_df['date'].dt.date.sort_values().unique()
            
            longest_streak = 0
            current_streak = 0
            
            if len(dates) > 0:
                current_streak = 1
                longest_streak = 1
                for i in range(1, len(dates)):
                    delta = dates[i] - dates[i-1]
                    if delta.days == 1:
                        current_streak += 1
                    else:
                        longest_streak = max(longest_streak, current_streak)
                        current_streak = 1
                longest_streak = max(longest_streak, current_streak)
            
            stats["longest_streak"] = longest_streak

            # 2. Most Productive Day
            # 0=Monday, 6=Sunday
            day_counts = self.commits_df['date'].dt.day_name().value_counts()
            if not day_counts.empty:
                stats["most_productive_day"] = day_counts.idxmax()

            # 3. Chronotype (Night Owl vs Early Bird)
            hours = self.commits_df['date'].dt.hour
            avg_hour = hours.mean()
            if avg_hour < 10:
                stats["chronotype"] = "🌅 Early Bird"
            elif avg_hour >= 20 or avg_hour < 4:
                stats["chronotype"] = "🦉 Night Owl"
            else:
                stats["chronotype"] = "☕ Day Walker"

            # 4. Most Active Month
            month_counts = self.commits_df['date'].dt.month_name().value_counts()
            if not month_counts.empty:
                stats["most_active_month"] = month_counts.idxmax()

        return stats

    def calculate_health_score(self, repo_data):
        files = repo_data.get("details", {}).get("files", [])
        score = 0
        missing = []
        
        checks = {
            "README.md": "README",
            "LICENSE": "License",
            "CONTRIBUTING.md": "Contributing Guide",
            ".gitignore": ".gitignore"
        }
        
        for file, name in checks.items():
            # Case insensitive check
            if any(f.lower() == file.lower() for f in files):
                score += 1
            else:
                missing.append(name)
        
        if score == 4: grade = "A"
        elif score == 3: grade = "B"
        elif score == 2: grade = "C"
        else: grade = "D"
        
        return {"grade": grade, "missing": missing, "score": score}

    def detect_tech_stack(self, repo_data):
        files = repo_data.get("details", {}).get("files", [])
        stack = []
        
        # Simple file-based detection
        if any(f == "package.json" for f in files): stack.append("Node.js")
        if any(f == "requirements.txt" or f == "pyproject.toml" for f in files): stack.append("Python")
        if any(f == "Dockerfile" for f in files): stack.append("Docker")
        if any(f == "docker-compose.yml" for f in files): stack.append("Docker Compose")
        if any(f == "pom.xml" for f in files): stack.append("Java")
        if any(f == "go.mod" for f in files): stack.append("Go")
        if any(f == "Cargo.toml" for f in files): stack.append("Rust")
        if any(f == "Gemfile" for f in files): stack.append("Ruby")
        
        return stack

    def get_timeline_events(self):
        events = []
        
        # 1. Joined GitHub
        if self.profile_data.get("created_at"):
            events.append({
                "date": pd.to_datetime(self.profile_data["created_at"]).strftime("%Y-%m-%d"),
                "title": "Joined GitHub",
                "icon": "🎉"
            })
            
        # 2. Repo Creation Milestones
        if self.repos_df is not None and not self.repos_df.empty:
            sorted_repos = self.repos_df.sort_values("created_at")
            
            # First Repo
            first_repo = sorted_repos.iloc[0]
            events.append({
                "date": first_repo["created_at"].strftime("%Y-%m-%d"),
                "title": f"First Repository Created: {first_repo['name']}",
                "icon": "🚀"
            })
            
            # Most Starred Repo
            most_starred = sorted_repos.loc[sorted_repos['stars'].idxmax()]
            if most_starred['stars'] > 0:
                events.append({
                    "date": most_starred["created_at"].strftime("%Y-%m-%d"), # Approximation: using creation date
                    "title": f"Created Most Starred Repo: {most_starred['name']} ({most_starred['stars']}⭐)",
                    "icon": "⭐"
                })
        
        # Sort by date
        events.sort(key=lambda x: x["date"])
        return events

    def forecast_activity(self):
        if not PROPHET_AVAILABLE:
            print("Forecasting disabled: prophet is not available.")
            return None
        if self.commits_df is None or self.commits_df.empty:
            return None

        # Prepare data for Prophet
        daily_counts = self.commits_df.set_index('date').resample('D').size().reset_index()
        daily_counts.columns = ['ds', 'y']
        
        # Prophet requires timezone-naive datetime
        daily_counts['ds'] = pd.to_datetime(daily_counts['ds']).dt.tz_localize(None)
        
        # Prophet requires at least 2 rows
        if len(daily_counts) < 2:
            return None

        m = Prophet(yearly_seasonality=True)
        m.fit(daily_counts)
        
        future = m.make_future_dataframe(periods=90) # Forecast 3 months
        forecast = m.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

if __name__ == "__main__":
    analyzer = TraditionalAnalyzer()
    if analyzer.load_data():
        print(analyzer.get_basic_stats())
        print(analyzer.perform_clustering())
