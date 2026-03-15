
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import json
import requests
from streamlit_lottie import st_lottie

# Add parent dir to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collection import GitHubFetcher
from src.llm_analysis import OllamaAnalyzer
from src.traditional_ds import TraditionalAnalyzer

st.set_page_config(page_title="Debug Dashboard", layout="wide")

# --- Localization Setup ---
def load_translations(lang_code):
    """Loads the JSON translation file for the specified language code, falling back to English for missing keys."""
    # Load English first as base
    base_path = os.path.join(os.path.dirname(__file__), '..', 'locales', 'en.json')
    translations = {}
    try:
        with open(base_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
    except Exception as e:
        st.error(f"Error loading base translations: {e}")

    if lang_code == 'en':
        return translations

    # Load selected language and update
    locale_path = os.path.join(os.path.dirname(__file__), '..', 'locales', f'{lang_code}.json')
    try:
        with open(locale_path, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
            translations.update(lang_data)
    except FileNotFoundError:
        pass # Just return English if file not found
    except Exception as e:
        # print(f"Error loading {lang_code} translations: {e}")
        pass
        
    # Temporary hardcoded fallback for Hindi if JSON is not generated yet
    if lang_code == "hi" and not translations.get("main_title") or translations.get("main_title") == "main_title":
        hi_fallback = {
            "main_title": "गिटहब डेवलपर डैशबोर्ड",
            "sidebar_header": "⚙️ कॉन्फ़िगरेशन",
            "username_label": "गिटहब यूजरनेम",
            "token_label": "गिटहब टोकन (वैकल्पिक)",
            "fetch_data_button": "⏳ डेटा प्राप्त करें",
            "fetching_spinner": "गिटहब से डेटा लाया जा रहा है...",
            "fetch_success": "✅ डेटा सफलतापूर्वक प्राप्त किया गया!",
            "fetch_error": "❌ डेटा प्राप्त करने में विफल।",
            "enter_username_info": "शुरू करने के लिए साइडबार में एक गिटहब यूजरनेम दर्ज करें।",
            "overview_header": "📊 अवलोकन",
            "tab_repos": "📦 रिपॉजिटरी",
            "tab_languages": "🔤 भाषाएं",
            "tab_llm": "🤖 एआई विश्लेषण",
            "tab_forecasting": "📈 पूर्वानुमान",
            "tab_model_comparison": "⚖️ मॉडल तुलना"
        }
        translations.update(hi_fallback)
        
    return translations

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def get_devicon_url(lang):
    mapping = {
        "python": "python", "javascript": "javascript", "typescript": "typescript",
        "html": "html5", "css": "css3", "java": "java", "c++": "cplusplus",
        "c": "c", "c#": "csharp", "php": "php", "ruby": "ruby", "go": "go", 
        "swift": "swift", "kotlin": "kotlin", "rust": "rust", "dart": "dart", 
        "scala": "scala", "r": "r", "shell": "bash", "vue": "vuejs",
        "react": "react", "angular": "angularjs"
    }
    mapped = mapping.get(lang.lower())
    if mapped:
        return f"https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{mapped}/{mapped}-original.svg"
    return None

# Language Selector
# For now, we manually list supported languages. Lingo.dev will generate the actual JSONs.
LANGUAGES = {
    "en": "English",
    "es": "Español",
    "fr": "Français", 
    "de": "Deutsch",
    "hi": "हिन्दी (Hindi)",
    "ja": "日本語 (Japanese)",
    "zh": "中文 (Chinese)",
    "pt": "Português",
    "ru": "Русский (Russian)",
    "ar": "العربية (Arabic)",
    "it": "Italiano",
    "ko": "한국어 (Korean)",
    "nl": "Nederlands",
    "tr": "Türkçe"
}

st.sidebar.header("Language")

if "selected_lang" not in st.session_state:
    st.session_state["selected_lang"] = "en"

selected_lang_code = st.sidebar.selectbox(
    "Select Language", 
    options=list(LANGUAGES.keys()), 
    format_func=lambda x: LANGUAGES[x],
    index=list(LANGUAGES.keys()).index(st.session_state["selected_lang"]),
    key="lang_selector"
)

st.session_state["selected_lang"] = selected_lang_code
translations = load_translations(st.session_state["selected_lang"])

def t(key, **kwargs):
    """
    Retrieves a translation for the given key.
    Supports simple string formatting via kwargs.
    Example: t("welcome_message", name="John")
    """
    text = translations.get(key, key) # Default to key if not found
    if text is None:
        return str(key)
        
    try:
        return str(text).format(**kwargs)
    except KeyError:
        return str(text) # Return unformatted text if kwargs are missing

# --- End Localization Setup ---


st.title(t("main_title"))

# --- Global Custom CSS for Glassmorphism & Badges ---
st.markdown("""
<style>
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
.tech-badge {
    display: inline-block;
    padding: 6px 12px;
    margin: 3px;
    border-radius: 20px;
    background: linear-gradient(135deg, #FF0080, #7928CA);
    color: white;
    font-size: 0.85em;
    font-weight: bold;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.user-avatar {
    border-radius: 50%;
    border: 3px solid #ff4b4b;
    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Sidebar for Configuration
st.sidebar.header(t("sidebar_header"))

# Initialize session state for inputs to prevent resetting
if "github_username" not in st.session_state:
    st.session_state["github_username"] = os.getenv("GITHUB_USERNAME", "")
if "github_token" not in st.session_state:
    st.session_state["github_token"] = os.getenv("GITHUB_TOKEN", "")

username = st.sidebar.text_input(t("username_label"), value=st.session_state["github_username"], key="user_input")
token = st.sidebar.text_input(t("token_label"), value=st.session_state["github_token"], type="password", key="token_input")

st.session_state["github_username"] = username
st.session_state["github_token"] = token

st.sidebar.caption("ℹ️ **Note:** Using a token ensures 100% accurate data and prevents missing repositories due to rate limits.")

with st.sidebar.expander("❓ How to get a GitHub Token?"):
    st.markdown("""
    1. Log in to [GitHub](https://github.com).
    2. Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
    3. Click **Generate new token (classic)**.
    4. Give it a name (e.g., "Dashboard").
    5. Select the **`repo`** and **`user`** scopes.
    6. Click **Generate token**.
    7. Copy the token and paste it here!
    """)

if st.sidebar.button(t("fetch_data_button")):
    if not token:
        st.sidebar.warning("⚠️ No token provided. Rate limit is 60 requests/hour. You may encounter errors.")
    
    lottie_search = load_lottieurl("https://lottie.host/8e2f8c5b-432d-4256-a14a-8d76dbd8b1e4/RAnJ9Yk7k9.json")
    if not lottie_search:
        lottie_search = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_fcfjwiyb.json")
    
    status_col1, status_col2 = st.sidebar.columns([1, 3])
    with status_col1:
        if lottie_search:
            st_lottie(lottie_search, height=50, key="fetching_lottie")
    with status_col2:
        st.markdown(f"**{t('fetching_spinner')}**")
        
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    def update_progress(count, total, current_repo):
        progress = count / total
        progress_bar.progress(progress)
        status_text.caption(f"🚀 Step {count}/{total}: `{current_repo}`")

    with st.spinner(t("fetching_spinner")):
        fetcher = GitHubFetcher(username=username, token=token)
        data = fetcher.fetch_all_data(progress_callback=update_progress)
        
        # Clear progress bar on completion
        progress_bar.empty()
        status_text.empty()

        if data:
            fetcher.save_data(data)
            st.toast(t("fetch_success"), icon="✅")
            st.sidebar.success(t("fetch_success"))
            st.balloons()
        else:
            st.sidebar.error(t("fetch_error") + " (Check terminal for details, likely rate limit)")

if not username:
    st.info(t("enter_username_info"))
    if not token:
        st.info("💡 **Tip:** Add a GitHub Token in the sidebar to increase your rate limit from 60 to 5000 requests/hour.")
    st.stop()

try:
    # Load Data
    analyzer = TraditionalAnalyzer()
    data_loaded = analyzer.load_data()
    
    # Check if data corresponds to the current user
    if data_loaded:
        loaded_user = analyzer.profile_data.get('login', '').lower()
        if loaded_user != username.lower():
            # Pass variables to translation string
            st.warning(t("cached_data_warning", loaded_user=loaded_user, username=username))
            # ALLOW MISMATCH FOR DEMO/PRESENTATION
            # st.stop()
    
    if not data_loaded:
        st.warning(t("no_data_warning"))
        st.stop()

    stats = analyzer.get_basic_stats()

    # User Avatar and Header Profile in Sidebar
    if analyzer.profile_data:
        avatar_url = analyzer.profile_data.get('avatar_url')
        if avatar_url:
            st.sidebar.markdown(f'''
            <div style="text-align: center; margin-top: -10px;">
                <img src="{avatar_url}" width="150" class="user-avatar" style="margin-bottom: 10px;">
                <h3 style="color: #ff4b4b; margin: 0;">{analyzer.profile_data.get('name', username)}</h3>
                <p style="color: #8b949e; font-size: 0.9em;">{analyzer.profile_data.get('bio', '')}</p>
            </div>
            <hr>
            ''', unsafe_allow_html=True)
            
        # Top Dashboard Banner
        st.subheader(f"👋 Welcome, {analyzer.profile_data.get('name', username)}!")
    else:
        st.subheader(f"👋 Welcome, {username}!")

    # Overview Section
    st.header(t("overview_header"))
    c1, c2, c3 = st.columns(3)
    # Tabs
    # Explicitly list tabs to avoid unpacking errors if numbers don't match
    tabs = st.tabs([
        t("tab_repos"), 
        t("tab_languages"), 
        t("tab_llm"), 
        t("tab_forecasting"), 
        t("tab_model_comparison"),
        "🎉 GitHub Replay",
        "📄 Resume Generator"
    ])
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5], tabs[6]

    with tab1:
        st.subheader(t("subheader_clustering"))
        
        # --- Repo Health & Tech Stack ---
        if analyzer.repos_df is not None and not analyzer.repos_df.empty:
            st.markdown(f"### {t('repo_health_header')}")
            
            # Use columns for a grid layout of repo cards
            # We'll show top 10 most recent or starred to avoid clutter, or a list
            # Let's show a list of cards
            
            # Need to get the full objects to pass to helper functions
            # Since repos_df has 'files' now (we updated load_data), we can construct it
            repos = analyzer.repos_df.to_dict('records')
            
            for repo in repos:
                 # Reconstruct repo_data structure expected by functions
                 # Structure: {"details": {"files": [...]}}
                 repo_data_struct = {"details": {"files": repo.get("files", [])}}
                 
                 health = analyzer.calculate_health_score(repo_data_struct)
                 stack = analyzer.detect_tech_stack(repo_data_struct)
                 
                 # Grade Color
                 grade_color = "#2ea043" if health['grade'] == 'A' else "#e3b341" if health['grade'] == 'B' else "#da3633"
                 
                 # Glass-card layout & Tech Badges with Devicons
                 badges = []
                 for s in stack:
                     icon_url = get_devicon_url(s)
                     if icon_url:
                         badges.append(f"<span class='tech-badge'><img src='{icon_url}' height='14' style='vertical-align: text-bottom; margin-right: 4px;' onerror='this.style.display=\"none\"'>{s}</span>")
                     else:
                         badges.append(f"<span class='tech-badge'>{s}</span>")
                         
                 badges_html = " ".join(badges) if badges else f"<span style='color:gray;font-size:0.8em;'>{t('no_stack_detected')}</span>"
                 missing_html = f"<br><span style='font-size:0.8em;color:#8b949e;'>{t('missing_label')}: {', '.join(health['missing'][:2])}</span>" if health['missing'] else ""
                 
                 card_html = f"""
<div class="glass-card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div style="flex: 2; padding-right: 15px; min-width: 250px;">
            <h3 style="margin-top:0; color:#58a6ff; margin-bottom:5px;">{repo['name']}</h3>
            <p style="color:#8b949e; margin-bottom:10px; font-size: 0.95em; line-height: 1.5; white-space: normal;">{repo.get('description', '') or 'No description provided.'}</p>
        </div>
        <div style="flex: 1; text-align: center; border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1); padding: 0 10px; min-width: 120px;">
            <div style="font-size: 0.85em; margin-bottom: 8px; color: #8b949e;">{t('health_label')}</div>
            <span style='color:{grade_color}; font-weight:bold; font-size:1.4em; border:2px solid {grade_color}; padding:6px 16px; border-radius:10px; display:inline-block;'>{health['grade']}</span>
            {missing_html}
        </div>
        <div style="flex: 1; text-align: center; padding-left: 15px; min-width: 150px;">
            <div style="margin-bottom: 8px; color: #8b949e; font-size: 0.85em;">Tech Stack</div>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 4px;">
                {badges_html}
            </div>
        </div>
    </div>
</div>
"""
                 st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info(t("clustering_info_no_data"))

    with tab2:
        st.subheader(t("subheader_language"))
        langs = stats.get("top_languages", {})
        if langs:
            import pandas as pd
            df_langs = pd.DataFrame(dict(r=list(langs.values()), theta=list(langs.keys())))
            fig = px.line_polar(df_langs, r='r', theta='theta', line_close=True, title=t("language_pie_title"), template="plotly_dark")
            fig.update_traces(fill='toself', line_color='#FF0080', fillcolor='rgba(255, 0, 128, 0.4)')
            st.plotly_chart(fig, use_container_width=True)
            # st.write("Chart disabled for debugging.")
        else:
            st.info(t("language_info_no_data"))

    with tab3:
        st.subheader(t("subheader_llm"))
        ollama_model = st.selectbox(t("select_model_label"), ["llama3.2:1b", "llama3.1", "mistral"])
        # Pass the full language name (e.g., "Spanish") to the analyzer
        target_lang_name = LANGUAGES[selected_lang_code]
        llm = OllamaAnalyzer(model_name=ollama_model, target_language=target_lang_name)

        if st.button(t("analyze_sentiment_button")):
            if analyzer.commits_df is not None and not analyzer.commits_df.empty:
                sample_commit = analyzer.commits_df.iloc[0]['message']
                st.write(f"**Sample Commit:** {sample_commit}")
                with st.spinner(t("sentiment_spinner")):
                    sentiment = llm.analyze_sentiment(sample_commit)
                    st.write(f"**Sentiment:** {sentiment}")
            else:
                st.info(t("no_commits_info"))

        st.markdown(t("skill_extraction_header"))
        if analyzer.repos_df is not None and not analyzer.repos_df.empty:
            repo_names = analyzer.repos_df['name'].tolist()
            selected_repo = st.selectbox(t("select_repo_label"), repo_names, key="skill_repo")
            
            if st.button(t("extract_skills_button")):
                repo_data = analyzer.repos_df[analyzer.repos_df['name'] == selected_repo].iloc[0]
                readme_text = repo_data.get('readme_content', "")
                
                if readme_text:
                    with st.spinner(t("extracting_spinner", repo=selected_repo)):
                        skills = llm.extract_skills(readme_text)
                        if skills and skills.startswith("Error:"):
                            st.error(skills)
                        elif skills:
                            st.success(t("skills_extracted_success"))
                            st.markdown(f"### {t('skills_extracted_success')}\n{skills}")
                        else:
                            st.warning(t("skills_extraction_failed"))

                else:
                    st.warning(t("no_readme_warning"))
            
            st.divider()
            st.subheader(t("ai_readme_header"))
            st.markdown(t("readme_improver_info"))
            
            if st.button(t("improve_readme_button")):
                repo_data = analyzer.repos_df[analyzer.repos_df['name'] == selected_repo].iloc[0]
                readme_text = repo_data.get('readme_content', "")
                if readme_text:
                    with st.spinner(f"Analyzing README for {selected_repo}..."):
                        tips = llm.analyze_readme_quality(readme_text)
                        if tips.startswith("Error:"):
                             st.error(tips)
                        else:
                             st.markdown(f"### {t('improvement_checklist_header')}")
                             st.markdown(tips)
                else:
                    st.warning(t("no_readme_to_improve"))

        else:
            st.info(t("clustering_info_no_data"))

    with tab4:
        st.subheader(t("subheader_forecasting"))
        if st.button(t("generate_forecast_button")):
            with st.spinner(t("forecasting_spinner")):
                try:
                    forecast = analyzer.forecast_activity()
                    if forecast is not None:
                        # Ensure 'ds' is datetime
                        forecast['ds'] = pd.to_datetime(forecast['ds'])
                        
                        fig = px.line(
                            forecast, 
                            x='ds', 
                            y='yhat', 
                            title=t("forecast_title"),
                            labels={'ds': 'Date', 'yhat': 'Predicted Actions'},
                            template="plotly_dark"
                        )
                        
                        # Style the main prediction line
                        fig.update_traces(line=dict(color="#ff4b4b", width=2.5))
                        
                        # Add smooth confidence intervals
                        fig.add_scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip')
                        fig.add_scatter(
                            x=forecast['ds'], 
                            y=forecast['yhat_upper'], 
                            fill='tonexty', 
                            mode='lines', 
                            line=dict(width=0), 
                            fillcolor='rgba(255, 75, 75, 0.2)', 
                            name='Confidence Interval',
                            hoverinfo='skip'
                        )
                        
                        # Clean up the layout to make it extremely readable
                        fig.update_layout(
                            xaxis_title="", 
                            yaxis_title="Expected GitHub Activity",
                            hovermode="x unified",
                            margin=dict(l=10, r=10, t=50, b=10),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(t("forecast_warning_not_enough"))
                except Exception as e:
                    st.error(t("forecast_error", error=str(e)))

    with tab5:
        st.subheader(t("subheader_comparison"))
        prompt = st.text_area(t("test_prompt_label"), "Summarize the coding style based on these commits...")
        if st.button(t("compare_button")):
            with st.spinner(t("comparison_spinner")):
                results = llm.compare_models(prompt)
                for model_name, metrics in results.items():
                    st.write(f"### {model_name}")
                    if "error" in metrics:
                        st.error(metrics["error"])
                    else:
                        st.write(f"**Time:** {metrics['time']:.2f}s")
                        st.write(f"**Response:** {metrics['response']}")
                        st.divider()

    with tab6:
        st.header(t("github_replay_header"))
        
        user_stats = analyzer.get_user_stats()
        
        # Generator Title logic
        if "user_title" not in st.session_state:
            with st.spinner(t("generating_persona_spinner")):
                target_lang_name = LANGUAGES[selected_lang_code]
                llm_replay = OllamaAnalyzer(model_name=ollama_model if 'ollama_model' in locals() else "llama3.1", target_language=target_lang_name)
                st.session_state["user_title"] = llm_replay.generate_user_title(user_stats)

        # --- Custom CSS for Cards ---
        st.markdown("""
        <style>
        .replay-card {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #58a6ff;
        }
        .metric-label {
            color: #8b949e;
            font-size: 1em;
        }
        .persona-title {
            font-size: 2.5em;
            background: -webkit-linear-gradient(45deg, #FF0080, #7928CA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        # --- Persona Section ---
        st.markdown(f"""
        <div class="replay-card">
            <div class="metric-label">{t("persona_label")}</div>
            <div class="persona-title">{st.session_state['user_title']}</div>
            <div style="margin-top: 10px; font-size: 1.2em;">{user_stats.get('chronotype', 'Day Walker')}</div>
        </div>
        """, unsafe_allow_html=True)

        # --- Metrics Grid ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="replay-card">
                <div class="metric-value">{user_stats.get('total_commits', 0)}</div>
                <div class="metric-label">{t("total_commits_label")}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="replay-card">
                <div class="metric-value">{user_stats.get('longest_streak', 0)} Days</div>
                <div class="metric-label">{t("longest_streak_label")}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="replay-card">
                <div class="metric-value">{user_stats.get('top_language', 'Unknown')}</div>
                <div class="metric-label">{t("top_language_label")}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="replay-card">
                <div class="metric-value">{user_stats.get('most_active_month', 'Unknown')[:3]}</div>
                <div class="metric-label">{t("peak_month_label")}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # --- Visualizations ---
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
             st.subheader(t("daily_activity_header"))
             if analyzer.commits_df is not None and not analyzer.commits_df.empty:
                 hourly_counts = analyzer.commits_df['date'].dt.hour.value_counts().sort_index()
                 st.bar_chart(hourly_counts)
                 # st.write("Chart disabled for debugging.")
             else:
                 st.info("No commit data available.")

        with col_viz2:
            st.subheader(t("top_languages_header"))
            langs = user_stats.get("top_languages", {}) # Note: get_user_stats currently doesn't return full dict, need to fix or use analyzer.get_basic_stats
            # Actually get_basic_stats has it.
            basic_stats = analyzer.get_basic_stats()
            top_langs = basic_stats.get("top_languages", {})
            if top_langs:
                st.bar_chart(pd.Series(top_langs).head(5))
                # st.write("Chart disabled for debugging.")
            else:
                st.info("No language data.")
        
        if st.button(t("generate_replay_button")):
             st.balloons()

        st.divider()
        st.subheader(t("my_github_journey_header"))
        
        timeline_events = analyzer.get_timeline_events()
        
        if timeline_events:
            # Custom HTML for Timeline
            timeline_html = """
            <style>
            .timeline {
                position: relative;
                max-width: 1200px;
                margin: 0 auto;
            }
            .timeline::after {
                content: '';
                position: absolute;
                width: 6px;
                background-color: #30363d;
                top: 0;
                bottom: 0;
                left: 31px;
                margin-left: -3px;
            }
            .container {
                padding: 10px 40px;
                position: relative;
                background-color: inherit;
                width: 100%;
            }
            .container::after {
                content: '';
                position: absolute;
                width: 25px;
                height: 25px;
                right: -17px;
                background-color: #58a6ff;
                border: 4px solid #0d1117;
                top: 15px;
                border-radius: 50%;
                z-index: 1;
                left: 18px;
            }
            .content {
                padding: 20px 30px;
                background-color: #161b22;
                position: relative;
                border-radius: 6px;
                border: 1px solid #30363d;
            }
            .date {
                font-size: 0.85em;
                color: #8b949e;
                margin-bottom: 5px;
            }
            .title {
                font-size: 1.1em;
                font-weight: bold;
                color: #c9d1d9;
            }
            </style>
            <div class="timeline">
            """
            
            for event in timeline_events:
                timeline_html += f"""
                <div class="container">
                    <div class="content">
                        <div class="date">{event['date']}</div>
                        <div class="title">{event['icon']} {event['title']}</div>
                    </div>
                </div>
                """
            
            timeline_html += "</div>"
            st.markdown(timeline_html, unsafe_allow_html=True)
        else:
            st.info(t("no_timeline_events"))

    with tab7:
        st.header(t("resume_generator_header"))
        st.markdown(t("resume_generator_info"))

        col_input, col_preview = st.columns([1, 1])

        with col_input:
            st.subheader(t("personal_details_header"))
            with st.form("resume_form"):
                col1, col2 = st.columns(2)
                with col1:
                    res_name = st.text_input(t("full_name_label"), value=analyzer.profile_data.get('name', ''))
                    res_email = st.text_input(t("email_label"), value=analyzer.profile_data.get('email', ''))
                    res_college = st.text_input(t("college_label"), placeholder="e.g. IIT Bombay")
                with col2:
                    res_title = st.text_input(t("professional_title_label"), value="Software Engineer")
                    res_linkedin = st.text_input(t("linkedin_label"))
                    res_cgpa = st.text_input(t("cgpa_label"), placeholder="e.g. 9.0/10")
                
                res_github = f"https://github.com/{analyzer.profile_data.get('login', '')}"
                st.text_input(t("github_url_label"), value=res_github, disabled=True)
                
                generate_btn = st.form_submit_button(t("generate_resume_button"))

        if generate_btn:
            lottie_build = load_lottieurl("https://lottie.host/7e040f7b-993d-4c32-b7a4-3158cabb0ea6/4w582w0eWe.json")
            if not lottie_build:
                lottie_build = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_bhebgw2x.json")
                
            res_col1, res_col2 = st.columns([1, 4])
            with res_col1:
                if lottie_build:
                    st_lottie(lottie_build, height=80, key="resume_lottie")
            with res_col2:
                st.info(f"**⚡ {t('analyzing_profile_spinner')}**")
                
            with st.spinner("AI is carefully assembling your skills and projects..."):
                # Prepare data for LLM
                stats = analyzer.get_basic_stats()
                user_stats = analyzer.get_user_stats()
                
                user_summary = f"Name: {res_name}, Bio: {analyzer.profile_data.get('bio', '')}, Repos: {stats.get('total_repos')}, Top Lang: {stats.get('top_languages')}"
                
                # Get top 20 repos for context to allow for more project selection
                top_repos = analyzer.repos_df.sort_values('stars', ascending=False).head(20)
                repo_summaries = []
                for _, row in top_repos.iterrows():
                    repo_summaries.append(f"- {row['name']}: {row['description']} (Lang: {row['language']})")
                
                repo_context = "\n".join(repo_summaries)
                
                # Generate JSON
                json_content_str = llm.generate_resume_content(user_summary, repo_context)
                
                if json_content_str and json_content_str.startswith("Error:"):
                    st.error(json_content_str)
                    json_content_str = None
                
                if json_content_str:
                    try:
                        resume_data = json.loads(json_content_str)
                        
                        # Add Manual/Calculated Fields
                        resume_data['name'] = res_name
                        resume_data['email'] = res_email
                        resume_data['title'] = res_title
                        resume_data['linkedin'] = res_linkedin
                        resume_data['github'] = res_github
                        
                        # New Fields: Education
                        resume_data['education'] = {
                            "college": res_college,
                            "cgpa": res_cgpa
                        }
                        
                        # New Fields: GitHub Stats
                        resume_data['github_stats'] = {
                            "streak": user_stats.get("longest_streak", 0),
                            "top_language": user_stats.get("top_language", "N/A"),
                            "total_repos": stats.get("total_repos", 0),
                            "joined": analyzer.profile_data.get("created_at", "N/A")[:10] if analyzer.profile_data.get("created_at") else "N/A"
                        }

                        st.session_state['resume_data'] = resume_data
                        st.success(t("resume_generated_success"))
                    except json.JSONDecodeError:
                        st.error("Failed to parse AI response. Please try again.")
                        st.text(json_content_str) # Debug
                else:
                    st.error(t("resume_generation_failed"))

        with col_preview:
            st.subheader(t("preview_download_header"))
            
            if 'resume_data' in st.session_state:
                data = st.session_state['resume_data']
                
                with st.container(border=True):
                    st.markdown(f"### 👤 {data.get('name', 'Your Name')}")
                    st.markdown(f"**{data.get('title', 'Software Engineer')}** | 📧 {data.get('email', '')}")
                    links = []
                    if data.get('linkedin'): links.append(f"🔗 [LinkedIn]({data.get('linkedin')})")
                    if data.get('github'): links.append(f"🐙 [GitHub]({data.get('github')})")
                    st.markdown(" | ".join(links))
                    
                    st.markdown("---")
                    
                    # Preview: Education and GitHub Stats
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader(t("education_header"))
                        edu = data.get('education', {})
                        st.markdown(f"**{edu.get('college', '')}**")
                        if edu.get('cgpa'):
                            st.markdown(f"_CGPA: {edu.get('cgpa')}_")
                    
                    with c2:
                        st.subheader(t("github_insights_header"))
                        gh = data.get('github_stats', {})
                        st.markdown(f"- **{t('longest_streak_label')}:** {gh.get('streak')} days")
                        st.markdown(f"- **{t('top_language_label')}:** {gh.get('top_language')}")
                        st.markdown(f"- **{t('metric_total_repos')}:** {gh.get('total_repos')}")
                    
                    st.markdown("---")

                    st.subheader(t("professional_summary_header"))
                    st.write(data.get('summary', ''))
                    
                    st.subheader(t("technical_skills_header"))
                    skills = data.get('top_skills', '')
                    if isinstance(skills, list):
                        skills = ", ".join(skills)
                    st.info(skills)
                    
                    st.subheader(t("key_projects_header"))
                    for project in data.get('projects', []):
                        st.markdown(f"#### {project.get('name', 'Untitled')}")
                        
                        tech = project.get('tech', [])
                        if isinstance(tech, list):
                            tech = " • ".join(tech)
                        st.markdown(f"_{tech}_")
                        
                        desc = project.get('description', [])
                        if isinstance(desc, list):
                            for item in desc:
                                st.markdown(f"- {item}")
                        else:
                            st.write(desc)
                        st.markdown("---")

                # PDF Generation
                import tempfile
                from src.resume_builder import ResumePDF # Local import to avoid top-level circular issues if any

                if st.button(t("download_pdf_button")):
                    try:
                        pdf = ResumePDF()
                        pdf.generate_resume(data, "resume.pdf")
                        
                        # Verify file exists
                        if os.path.exists("resume.pdf"):
                            with open("resume.pdf", "rb") as f:
                                st.download_button(
                                    label=t("click_to_download_label"),
                                    data=f,
                                    file_name=f"{data.get('name', 'resume').replace(' ', '_')}_Resume.pdf",
                                    mime="application/pdf"
                                )
                            st.success(t("pdf_ready_success"))
                        else:
                            st.error("PDF file was not created.")
                    except Exception as e:
                        st.error(t("pdf_creation_error", error=str(e)))
            else:
                st.info(t("fill_details_info"))

except Exception as e:
    st.error(t("error_occurred", error=str(e)))
    import traceback
    st.text(traceback.format_exc())
