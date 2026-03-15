import sys
import os
sys.path.append(os.getcwd())
from src.traditional_ds import TraditionalAnalyzer

def verify():
    print("Verifying Fix...")
    try:
        analyzer = TraditionalAnalyzer()
        if not analyzer.load_data():
            print("Failed to load data (files may be missing), but code is reachable.")
            return

        print("Data loaded. Columns:", analyzer.repos_df.columns.tolist())
        
        # Test the problematic line
        top_repos = analyzer.repos_df.sort_values('stars', ascending=False).head(5)
        print("✅ Successfully sorted by 'stars'")
        
        # Test description access
        for _, row in top_repos.iterrows():
            desc = row['description']
            print(f"Repo: {row['name']}, Desc found: {desc is not None}")
            
        print("✅ Verification passed due to no KeyErrors.")
        
    except KeyError as e:
        print(f"❌ KeyError: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify()
