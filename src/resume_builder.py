from fpdf import FPDF

class ResumePDF(FPDF):
    def header(self):
        # We don't want a repeating header on every page for a resume usually,
        # but if we did, it would go here.
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_custom_header(self, name, email, linkedin=None, github=None, title="Software Engineer"):
        self.set_font('Arial', 'B', 20) # Slightly smaller
        self.cell(0, 8, name, 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        
        contact_info = f"{title}  |  {email}"
        if linkedin:
            contact_info += f"  |  LinkedIn"
        if github:
            contact_info += f"  |  GitHub"
            
        self.cell(0, 5, contact_info, 0, 1, 'C')
        
        # Add a line
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y()+2, 200, self.get_y()+2)
        self.ln(8) # Relaxed spacing

    def add_section_title(self, title):
        self.set_font('Arial', 'B', 12) # Smaller title
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, title.upper(), 0, 1) # Reduced height
        
        # Underline
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3) # Slightly relaxed
        self.set_text_color(0, 0, 0)

    def add_summary_section(self, summary_text):
        self.add_section_title("Professional Summary")
        self.set_font('Arial', '', 10) # 10pt font
        self.multi_cell(0, 4, summary_text) # Tighter line height
        self.ln(4) # Relaxed

    def add_skills_section(self, skills_list):
        self.add_section_title("Technical Skills")
        
        if isinstance(skills_list, list):
            skills_text = ", ".join(skills_list)
        else:
            skills_text = skills_list
        
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 4, skills_text)
        self.ln(4) # Relaxed

    def add_project_section(self, projects):
        """
        projects: list of dicts with 'name', 'tech', 'description'
        """
        self.add_section_title("Key Projects")
        
        for project in projects:
            self.set_font('Arial', 'B', 10) # 10pt bold
            
            # Combine Name and Tech on one line if possible, or just tight spacing
            name = project.get('name', 'Untitled')
            tech = project.get('tech', '')
            if isinstance(tech, list):
                tech = ", ".join(tech)
            
            if tech:
                title_line = f"{name}  --  {tech}"
            else:
                title_line = name
                
            self.cell(0, 5, title_line, 0, 1)
            
            self.set_font('Arial', '', 9.5) # Slightly smaller body
            self.set_text_color(0, 0, 0)
            
            desc = project.get('description', '')
            if isinstance(desc, list):
                for item in desc:
                     self.cell(4) # Indent
                     self.cell(0, 4, f"- {item}", 0, 1) # Single line bullets preferred
            elif desc:
                self.multi_cell(0, 4, desc)
            self.ln(3) # Relaxed spacing between projects

    def add_education_section(self, education):
        if not education or not education.get('college'):
            return

        self.add_section_title("Education")
        self.set_font('Arial', 'B', 10)
        
        text = education.get('college')
        if education.get('cgpa'):
            text += f"  (CGPA: {education.get('cgpa')})"
            
        self.cell(0, 5, text, 0, 1)
        self.ln(3)

    def add_github_stats_section(self, stats):
        if not stats:
            return
            
        self.add_section_title("GitHub Achievements")
        self.set_font('Arial', '', 9)
        
        stat_items = []
        if stats.get('top_language'): stat_items.append(f"Top Lang: {stats.get('top_language')}")
        if stats.get('streak'): stat_items.append(f"Streak: {stats.get('streak')} Days")
        if stats.get('total_repos'): stat_items.append(f"Repos: {stats.get('total_repos')}")
        if stats.get('joined'): stat_items.append(f"Joined: {stats.get('joined')}")
            
        stats_text = "   |   ".join(stat_items)
        self.cell(0, 5, stats_text, 0, 1, 'C') # Changed to cell for tightness
        self.ln(3)

    def generate_resume(self, user_data, output_path):
        self.add_page()
        
        # Header
        self.add_custom_header(
            user_data.get('name', ''),
            user_data.get('email', ''),
            user_data.get('linkedin', ''),
            user_data.get('github', ''),
            user_data.get('title', '')
        )
        
        # Summary
        if user_data.get('summary'):
            self.add_summary_section(user_data.get('summary'))
            
        # Education
        if user_data.get('education'):
            self.add_education_section(user_data['education'])
            
        # GitHub Stats
        if user_data.get('github_stats'):
            self.add_github_stats_section(user_data['github_stats'])
            
        # Skills
        if user_data.get('top_skills'):
            self.add_skills_section(user_data.get('top_skills'))
            
        # Projects
        if user_data.get('projects'):
            self.add_project_section(user_data.get('projects'))
            
        self.output(output_path)
