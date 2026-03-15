import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import json

# Add parent dir to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Debug Dashboard", layout="wide")
print("DEBUG: App started")
st.write("DEBUG: App started (UI)")

try:
    from src.data_collection import GitHubFetcher
    from src.llm_analysis import OllamaAnalyzer
    from src.traditional_ds import TraditionalAnalyzer
    print("DEBUG: Imports successful")
    st.write("DEBUG: Imports successful (UI)")
except Exception as e:
    print(f"DEBUG: Import failed: {e}")
    st.error(f"Import failed: {e}")

st.title("Debug Dashboard")

username = os.getenv("GITHUB_USERNAME", "testuser")
print(f"DEBUG: Username: {username}")
st.write(f"DEBUG: Username: {username} (UI)")

if st.button("Load Data"):
    try:
        print("DEBUG: Loading data...")
        analyzer = TraditionalAnalyzer()
        data_loaded = analyzer.load_data()
        print(f"DEBUG: Data loaded: {data_loaded}")
        st.write(f"Data loaded: {data_loaded}")
        
        if data_loaded:
            stats = analyzer.get_basic_stats()
            print(f"DEBUG: Stats: {stats}")
            st.write(stats)
    except Exception as e:
        print(f"DEBUG: Data load failed: {e}")
        st.error(f"Data load failed: {e}")

st.write("End of script")
