import ollama
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class OllamaAnalyzer:
    def __init__(self, model_name="llama3.2:1b", target_language="English"):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.model = model_name
        self.target_language = target_language

    def analyze_sentiment(self, text):
        prompt = f"Analyze the sentiment of the following commit message. Return only 'Positive', 'Neutral', or 'Negative' in {self.target_language}.\n\nCommit Message: {text}"
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return "Error"

    def extract_skills(self, readme_content):
        prompt = f"Extract a list of technical skills, languages, and frameworks mentioned in the following README content. Return them as a comma-separated list in {self.target_language}.\n\nREADME:\n{readme_content[:2000]}" # Limit context
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error in skill extraction: {e}")
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                return "Error: Ollama is not running. Please start it."
            return f"Error: {str(e)}"

    def classify_topic(self, repo_description):
        prompt = f"Classify the following repository description into one of these topics: 'Web Development', 'Data Science', 'Machine Learning', 'Mobile App', 'DevOps', 'Other'. Return only the topic name in {self.target_language}.\n\nDescription: {repo_description}"
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error in topic classification: {e}")
            return "Other"

    def compare_models(self, task_prompt, models=["llama3.1", "mistral"]):
        results = {}
        for model in models:
            start_time = time.time()
            try:
                # Append language instruction to the user's prompt
                full_prompt = f"{task_prompt}\n\nPlease respond in {self.target_language}."
                response = self.client.chat(model=model, messages=[
                    {'role': 'user', 'content': full_prompt}
                ])
                duration = time.time() - start_time
                results[model] = {
                    "response": response['message']['content'],
                    "time": duration
                }
            except Exception as e:
                results[model] = {"error": str(e)}
        return results

    def generate_user_title(self, stats):
        prompt = f"""Based on the following GitHub stats, generate a creative, fun, RPG-style user title (max 5 words) in {self.target_language}.
        Return ONLY the title.
        Stats:
        - Top Language: {stats.get('top_language')}
        - Longest Streak: {stats.get('longest_streak')} days
        - Most Productive Day: {stats.get('most_productive_day')}
        """
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip().replace('"', '')
        except Exception as e:
            print(f"Error generating title: {e}")
            return "The GitHub Wanderer"

    def analyze_readme_quality(self, readme_content):
        prompt = f"""Analyze the quality of this README file.
        Provide a checklist of 3-5 improvements in {self.target_language}. Focus on missing standard sections (Installation, Usage, Contributing, License).
        Keep it concise and actionable.
        README Content (first 2000 chars):
        {readme_content[:2000]}
        """
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error analyzing README: {e}")
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                return "Error: Ollama is not running. Please start it."
            return f"Error: {str(e)}"

    def generate_resume_content(self, user_profile, repo_summaries):
        """
        Generates structured resume content (Summary, top skills, specific project descriptions)
        based on aggregated GitHub data.
        """
        # Enhanced prompt to discourage common JSON errors
        prompt = f"""
        You are an elite technical resume writer. 
        Create a highly professional, detailed, and impactful resume content based on this GitHub profile data in {self.target_language}.
        
        User: {user_profile}
        Repositories (Top 10): {repo_summaries}
        
        Return a valid JSON object with EXACTLY these keys:
        - "summary": A compelling 4-5 sentence professional summary highlighting technical expertise, achievements, and career goals.
        - "top_skills": A comprehensive list of technical skills (languages, frameworks, tools), comma-separated.
        - "projects": A list of 7-8 standout objects.
            - "name": Project Name
            - "tech": List of technologies used
            - "description": A list of 1-2 concise, punchy bullet points. Focus purely on impact. Keep them short to ensure the resume fits on one page.
        
        IMPORTANT:
        - Output ONLY valid JSON.
        - Do NOT include markdown formatting (like ```json).
        - Do NOT include trailing commas.
        - Do NOT include comments.
        """
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            content = response['message']['content'].strip()
            return self._clean_and_parse_json(content)
            
        except Exception as e:
            print(f"Error generating resume content: {e}")
            return json.dumps({"error": str(e)})

    def _clean_and_parse_json(self, content):
        import json
        import re
        
        # 1. Strip Markdown Code Blocks
        if "```" in content:
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
        
        # 2. Extract JSON object
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
            
        # 3. Fix Trailing Commas (Common LLM Error)
        # Replaces ", }" with "}" and ", ]" with "]"
        content = re.sub(r',\s*\}', '}', content)
        content = re.sub(r',\s*\]', ']', content)
        
        return content


if __name__ == "__main__":
    analyzer = OllamaAnalyzer()
    print("Testing connection...")
    try:
        print(analyzer.analyze_sentiment("Initial commit - added core features"))
    except Exception as e:
        print(f"Ollama connection failed: {e}")
