
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd()))

from src.llm_analysis import OllamaAnalyzer
from src.data_collection import GitHubFetcher
from src.traditional_ds import TraditionalAnalyzer

def test_resume_generation():
    print("Initializing Analyzer...")
    try:
        analyzer = TraditionalAnalyzer()
        # Mock data if needed, or load if available
        if not analyzer.load_data():
            print("No data found. fetching mock data or cannot proceed.")
            return

        stats = analyzer.get_basic_stats()
        user_stats = analyzer.get_user_stats()
        
        user_summary = f"Name: Test User, Bio: Bio, Repos: {stats.get('total_repos')}, Top Lang: {stats.get('top_languages')}"
        
        if analyzer.repos_df is not None and not analyzer.repos_df.empty:
            top_repos = analyzer.repos_df.sort_values('stars', ascending=False).head(10)
            repo_summaries = []
            for _, row in top_repos.iterrows():
                repo_summaries.append(f"- {row['name']}: {row['description']} (Lang: {row['language']})")
            repo_context = "\n".join(repo_summaries)
        else:
            repo_context = "No repositories found."

        print("Initializing LLM...")
        llm = OllamaAnalyzer(model_name="llama3.2:1b", target_language="English")
        
        print("Target Language: English")
        print("Model: llama3.2:1b")
        print("Generating resume content...")
        
        content = llm.generate_resume_content(user_summary, repo_context)
        
        print("\n--- Result ---")
        print(content)
        
    except Exception as e:
        print(f"\n--- Exception Caught ---")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_resume_generation()
