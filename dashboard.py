import streamlit as st

# Page Config MUST be the first Streamlit command
st.set_page_config(
    page_title="GitHub AI Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
from datetime import datetime

# Local Imports
try:
    from src.data_collection import GitHubFetcher
    from src.traditional_ds import TraditionalAnalyzer
    from src.llm_analysis import OllamaAnalyzer
    from src.resume_builder import ResumePDF
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# --- Internationalization ---
def load_locale(lang_code):
    try:
        with open(f"locales/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Language Selector (default to en)
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Sidebar Configuration
with st.sidebar:
    st.header("🌐 Language")
    
    # Map friendly names to codes
    lang_options = {
        "English": "en",
        "Español": "es",
        "Français": "fr",
        "Deutsch": "de"
    }
    
    selected_lang_name = st.selectbox(
        "Select Language / Seleccionar Idioma",
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(st.session_state.language)
    )
    
    # Update session state if changed
    st.session_state.language = lang_options[selected_lang_name]

# Load translations for selected language
t = load_locale(st.session_state.language)
# Fallback to English for missing keys
t_en = load_locale("en")

def txt(key, **kwargs):
    """Get translation with fallback and formatting."""
    text = t.get(key, t_en.get(key, f"MISSING: {key}"))
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

# Initialize LLM with selected language and model
# Default to lightweight model for CPU/Low RAM systems
if 'model_name' not in st.session_state:
    st.session_state.model_name = "llama3.2:1b"

llm = OllamaAnalyzer(model_name=st.session_state.model_name, target_language=selected_lang_name)

# --- Application Logic ---

# Sidebar - Inputs
with st.sidebar:
    st.header(txt("sidebar_header"))
    username = st.text_input(txt("username_label"), value=st.session_state.get('last_username', ''))
    token = st.text_input(txt("token_label"), type="password")
    
    with st.expander("ℹ️ How to get a GitHub Token?"):
        st.markdown("""
        1. Go to [GitHub Developer Settings](https://github.com/settings/tokens)
        2. Click **Generate new token (classic)**
        3. Add a note and select scopes: `repo` and `user`
        4. Apply and copy the generated token here
        """)
    
    if st.button(txt("fetch_data_button"), type="primary"):
        if not username:
            st.warning(txt("enter_username_info"))
        else:
            with st.spinner(txt("fetching_spinner")):
                fetcher = GitHubFetcher(username=username, token=token)
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                def update_progress(current, total, repo_name):
                    progress = int((current / total) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Analyzing {repo_name}... ({current}/{total})")
                
                data = fetcher.fetch_all_data(progress_callback=update_progress)
                progress_bar.empty()
                status_text.empty()
                
                if data:
                    st.session_state.data = data
                    st.session_state.last_username = username
                    fetcher.save_data(data)
                    st.success(txt("fetch_success"))
                    st.rerun()
                else:
                    st.error(txt("fetch_error"))

# Main Content
st.title(txt("main_title"))

if 'data' not in st.session_state or not st.session_state.data:
    st.info(txt("no_data_warning"))
    st.stop()

# Data is ready
raw_data = st.session_state.data
profile = raw_data.get("profile", {})
analyzer = TraditionalAnalyzer("data/raw_data.json")
analyzer.load_data()

# Warn if viewing cached data for different user
if st.session_state.get('last_username') and profile.get('login') and st.session_state.last_username.lower() != profile.get('login').lower():
    st.warning(txt("cached_data_warning", loaded_user=profile.get('login'), username=st.session_state.last_username))

# Profile Header
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    st.image(profile.get('avatar_url', ''), width=100)
with c2:
    st.subheader(profile.get('name', 'Unknown'))
    st.write(profile.get('bio', ''))
    st.caption(f"📍 {profile.get('location', '')} | 🔗 [{txt('github_url_label')}]({profile.get('html_url', '')})")

# Tabs
tabs = st.tabs([
    txt("overview_header"), 
    txt("tab_llm"),
    txt("github_replay_header"),
    txt("resume_generator_header"),
    txt("tab_forecasting")
])

# --- Tab 1: Overview ---
with tabs[0]:
    stats = analyzer.get_basic_stats()
    
    # Custom CSS for KPI Cards
    st.markdown("""
    <style>
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
        margin-bottom: 20px;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
        display: inline-block;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 5px;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📁</div>
            <div class="kpi-value">{{stats.get('total_repos', 0)}}</div>
            <div class="kpi-label">{{txt("metric_total_repos")}}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⭐</div>
            <div class="kpi-value">{{stats.get('total_stars', 0)}}</div>
            <div class="kpi-label">{{txt("metric_total_stars")}}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🔄</div>
            <div class="kpi-value">{{stats.get('total_commits_tracked', 0)}}</div>
            <div class="kpi-label">{{txt("metric_commits_tracked")}}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.subheader(txt("subheader_language"))
        langs = stats.get('top_languages', {})
        if langs:
            # Take top 6 languages for the radar chart to avoid crowding
            top_langs = dict(list(langs.items())[:6])
            df_langs = pd.DataFrame({'Language': list(top_langs.keys()), 'Count': list(top_langs.values())})
            
            fig = px.line_polar(
                df_langs, 
                r='Count', 
                theta='Language', 
                line_close=True,
                color_discrete_sequence=['#8b5cf6']
            )
            fig.update_traces(fill='toself', opacity=0.6)
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=False, showticklabels=False),
                    angularaxis=dict(tickfont=dict(size=14, color="#e2e8f0"), gridcolor='rgba(255, 255, 255, 0.1)')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(txt("language_info_no_data"))
            
    with col_2:
        st.subheader(txt("subheader_clustering"))
        clustered_df = analyzer.perform_clustering()
        if clustered_df is not None:
            fig = px.scatter(clustered_df, x='stars', y='forks', color='cluster', hover_name='name', size='stars', title=txt("clusters_title"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(txt("clustering_info_not_enough"))

# --- Tab 2: LLM Insights ---
with tabs[1]:
    st.subheader(txt("subheader_llm"))
    
    # 1. Repo Selector
    repo_names = analyzer.repos_df['name'].tolist() if analyzer.repos_df is not None else []
    selected_repo = st.selectbox(txt("select_repo_label"), repo_names)
    
    c_a, c_b = st.columns(2)
    
    # Commit Analysis
    with c_a:
        st.markdown("### Commit Sentiment")
        if st.button(txt("analyze_sentiment_button")):
            with st.spinner(txt("sentiment_spinner")):
                # Get a recent commit message
                commits = analyzer.commits_df
                if commits is not None and not commits.empty and selected_repo:
                    repo_commits = commits[commits['repo_name'] == selected_repo]
                    if not repo_commits.empty:
                        msg = repo_commits.iloc[0]['message']
                        st.write(f"Commit: *{msg}*")
                        sentiment = llm.analyze_sentiment(msg)
                        st.success(sentiment)
                    else:
                        st.info(txt("no_commits_info"))
                else:
                    st.info(txt("no_commits_info"))

    # Skill Extraction
    with c_b:
        st.markdown(txt("skill_extraction_header"))
        if st.button(txt("extract_skills_button")):
            with st.spinner(txt("extracting_spinner", repo=selected_repo)):
                repo_data = analyzer.repos_df[analyzer.repos_df['name'] == selected_repo].iloc[0]
                readme = repo_data.get('readme_content', '')
                if readme:
                    skills = llm.extract_skills(readme)
                    st.success(txt("skills_extracted_success"))
                    st.write(skills)
                else:
                    st.warning(txt("no_readme_warning"))

    st.markdown("---")
    
    # README Improver
    st.markdown(txt("ai_readme_header"))
    if st.button(txt("improve_readme_button")):
         with st.spinner(txt("analyzing_profile_spinner")):
            repo_data = analyzer.repos_df[analyzer.repos_df['name'] == selected_repo].iloc[0]
            readme = repo_data.get('readme_content', '')
            if readme:
                audit = llm.analyze_readme_quality(readme)
                st.markdown(audit)
            else:
                st.warning(txt("no_readme_to_improve"))

# --- Tab 3: GitHub Replay ---
with tabs[2]:
    st.header(txt("github_replay_header"))
    user_stats = analyzer.get_user_stats()
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(txt("top_language_label"), user_stats.get('top_language'))
        st.metric(txt("longest_streak_label"), f"{user_stats.get('longest_streak')} Days")
    
    with col_r2:
        st.metric(txt("peak_month_label"), user_stats.get('most_active_month'))
        st.metric("Chronotype", user_stats.get('chronotype'))
        
    st.markdown("### " + txt("persona_label"))
    if st.button(txt("generate_replay_button")):
        with st.spinner(txt("generating_persona_spinner")):
             title = llm.generate_user_title(user_stats)
             st.markdown(f"# 🎭 {title}")

# --- Tab 4: Resume Generator ---
with tabs[3]:
    st.header(txt("resume_generator_header"))
    st.info(txt("resume_generator_info"))
    
    with st.form("resume_form"):
        st.subheader(txt("personal_details_header"))
        c1, c2 = st.columns(2)
        r_name = c1.text_input(txt("full_name_label"), value=profile.get("name", ""))
        r_email = c2.text_input(txt("email_label"), value=profile.get("email") or "your.email@example.com")
        
        c3, c4 = st.columns(2)
        r_cologs = c3.text_input(txt("college_label"), "University of Tech")
        r_cgpa = c4.text_input(txt("cgpa_label"), "3.8/4.0")
        
        r_linkedin = st.text_input(txt("linkedin_label"), profile.get("blog") or "")
        
        submit_resume = st.form_submit_button(txt("generate_resume_button"))
    
    if submit_resume:
        with st.spinner(txt("analyzing_profile_spinner")):
            # Get data
            top_repos = analyzer.repos_df.sort_values('stars', ascending=False).head(5)['name'].tolist() if analyzer.repos_df is not None else []
            repo_summaries = ", ".join(top_repos)
            
            # Generate content
            content_json_str = llm.generate_resume_content(r_name, repo_summaries)
            
            try:
                # Parse JSON
                resume_content = json.loads(content_json_str)
                
                # Construct data dict
                resume_data = {
                    "name": r_name,
                    "email": r_email,
                    "linkedin": r_linkedin,
                    "github": f"github.com/{username}",
                    "title": "Software Engineer", 
                    "summary": resume_content.get("summary"),
                    "top_skills": resume_content.get("top_skills"),
                    "projects": resume_content.get("projects"),
                    "education": {"college": r_cologs, "cgpa": r_cgpa},
                    "github_stats": {
                        "top_language": user_stats.get("top_language"),
                        "streak": user_stats.get("longest_streak"),
                        "total_repos": raw_data.get("public_repos")
                    }
                }
                
                # Generate PDF
                pdf = ResumePDF()
                pdf.generate_resume(resume_data, "resume.pdf")
                
                st.success(txt("pdf_ready_success"))
                
                with open("resume.pdf", "rb") as f:
                    st.download_button(
                        label=txt("download_pdf_button"),
                        data=f,
                        file_name=f"{username}_resume.pdf",
                        mime="application/pdf"
                    )
                    
            except Exception as e:
                st.error(txt("resume_generation_failed"))
                st.error(e)
                st.expander("Debug").write(content_json_str)

# --- Tab 5: Forecasting ---
with tabs[4]:
    st.header(txt("subheader_forecasting"))
    
    if st.button(txt("generate_forecast_button")):
        with st.spinner(txt("forecasting_spinner")):
            forecast = analyzer.forecast_activity()
            if forecast is not None:
                fig = px.line(forecast, x='ds', y='yhat', title=txt("forecast_title"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(txt("forecast_warning_not_enough"))
