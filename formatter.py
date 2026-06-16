import os
import re
import io
import requests
from PIL import Image
from fpdf import FPDF
from bs4 import BeautifulSoup

class CodelabFormatter:
    @staticmethod
    def sanitize_text(text):
        if not text:
            return ""
        # Replace common unicode punctuation with ASCII equivalents
        replacements = {
            "\u201c": '"',  # Left double quotation mark
            "\u201d": '"',  # Right double quotation mark
            "\u2018": "'",  # Left single quotation mark
            "\u2019": "'",  # Right single quotation mark
            "\u2013": "-",  # En dash
            "\u2014": "--", # Em dash
            "\u2022": "*",  # Bullet
            "\u2026": "...",# Ellipsis
            "\u00a0": " ",  # Non-breaking space
            "\u200b": "",   # Zero-width space
            "\u2028": "\n", # Line separator
            "\u2029": "\n", # Paragraph separator
            "\u00a9": "(c)",# Copyright
            "\u00ae": "(r)",# Registered
            "\u2122": "(tm)",# Trademark
        }
        for search, replace in replacements.items():
            text = text.replace(search, replace)
        # Fallback: encode to latin-1 ignoring unsupported characters, then decode
        return text.encode('latin-1', errors='ignore').decode('latin-1')

    @staticmethod
    def to_html(data):
        """
        Generates a single, beautiful, and interactive HTML document
        containing all scraped steps and styling (with dark mode support).
        """
        title = data.get("title", "Codelab")
        authors = data.get("authors", "")
        last_updated = data.get("last_updated", "")
        total_duration = data.get("total_duration", 0)
        source_url = data.get("source_url", "")
        
        steps_html = ""
        sidebar_items = ""
        
        for step in data.get("steps", []):
            idx = step["index"]
            step_title = step["title"]
            duration = step["duration"]
            content = step["content_html"]
            
            sidebar_items += f'<a href="#step-{idx}" class="sidebar-link" id="link-{idx}">{idx + 1}. {step_title}</a>'
            
            steps_html += f"""
            <section id="step-{idx}" class="codelab-step">
                <div class="step-header">
                    <h2 class="step-title">{idx + 1}. {step_title}</h2>
                    <span class="step-duration"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> {duration} mins</span>
                </div>
                <div class="step-content">
                    {content}
                </div>
            </section>
            """
            
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Google Codelab</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f8fafc;
            --container-bg: #ffffff;
            --text-color: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --primary: #1a73e8;
            --primary-hover: #1557b0;
            --primary-light: #e8f0fe;
            --code-bg: #1e1e2e;
            --code-text: #cdd6f4;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.05), 0 4px 6px -4px rgb(0 0 0 / 0.05);
        }}

        body.dark-mode {{
            --bg-color: #000000;
            --container-bg: #121212;
            --text-color: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #27272a;
            --primary: #3b82f6;
            --primary-hover: #60a5fa;
            --primary-light: #1e3a8a;
            --code-bg: #09090b;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.5);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.6);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: background-color 0.3s, color 0.3s;
        }}

        /* Header styling */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: var(--container-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow);
            transition: background-color 0.3s, border-color 0.3s;
        }}

        .header-title-container {{
            max-width: 70%;
        }}

        .header-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .header-meta {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .header-actions {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .btn {{
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.875rem;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background-color: var(--container-bg);
            color: var(--text-color);
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn:hover {{
            background-color: var(--bg-color);
            border-color: var(--text-secondary);
        }}

        .btn-primary {{
            background-color: var(--primary);
            color: #ffffff;
            border: none;
        }}

        .btn-primary:hover {{
            background-color: var(--primary-hover);
            color: #ffffff;
        }}

        /* App Layout */
        .app-container {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            min-height: calc(100vh - 70px);
        }}

        /* Sidebar Navigation */
        .sidebar {{
            width: 320px;
            border-right: 1px solid var(--border-color);
            padding: 2rem 1.5rem;
            position: sticky;
            top: 70px;
            height: calc(100vh - 70px);
            overflow-y: auto;
            background-color: var(--container-bg);
            transition: background-color 0.3s, border-color 0.3s;
        }}

        .sidebar-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 1rem;
            font-weight: 700;
        }}

        .sidebar-link {{
            display: block;
            padding: 0.75rem 1rem;
            color: var(--text-color);
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            font-weight: 500;
        }}

        .sidebar-link:hover {{
            background-color: var(--bg-color);
            padding-left: 1.25rem;
        }}

        .sidebar-link.active {{
            background-color: var(--primary-light);
            color: var(--primary);
            border-left-color: var(--primary);
        }}

        /* Content Panel */
        .content-panel {{
            flex: 1;
            padding: 3rem 4rem;
            overflow-y: auto;
            max-width: 900px;
            margin: 0 auto;
        }}

        .codelab-step {{
            margin-bottom: 5rem;
            scroll-margin-top: 100px;
        }}

        .step-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
            transition: border-color 0.3s;
        }}

        .step-title {{
            font-size: 1.75rem;
            font-weight: 700;
        }}

        .step-duration {{
            background-color: var(--bg-color);
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border: 1px solid var(--border-color);
        }}

        .step-content {{
            font-size: 1.05rem;
        }}

        .step-content p {{
            margin-bottom: 1.25rem;
        }}

        /* Callout boxes */
        .callout {{
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            margin: 1.5rem 0;
            border-left: 5px solid;
            font-size: 0.975rem;
        }}

        .callout-note {{
            background-color: #f0f7ff;
            border-color: #1a73e8;
            color: #185abc;
        }}
        body.dark-mode .callout-note {{
            background-color: #1e293b;
            border-color: #3b82f6;
            color: #60a5fa;
        }}

        .callout-warning {{
            background-color: #fce8e6;
            border-color: #d93025;
            color: #a51d24;
        }}
        body.dark-mode .callout-warning {{
            background-color: #2d1f1f;
            border-color: #ef4444;
            color: #f87171;
        }}

        /* Code blocks */
        pre {{
            background-color: var(--code-bg);
            color: var(--code-text);
            padding: 1.25rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 0.9rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }}

        code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9em;
            background-color: var(--bg-color);
            padding: 0.15rem 0.35rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            color: inherit;
        }}

        /* Lists */
        .step-content ul, .step-content ol {{
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }}

        .step-content li {{
            margin-bottom: 0.5rem;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: var(--shadow);
            border-radius: 8px;
            overflow: hidden;
        }}

        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background-color: var(--bg-color);
            font-weight: 600;
        }}

        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            display: block;
            margin: 1.5rem auto;
            box-shadow: var(--shadow-lg);
        }}

        @media (max-width: 992px) {{
            .sidebar {{
                display: none;
            }}
            .content-panel {{
                padding: 2rem;
            }}
        }}
    </head>
<body class="dark-mode">
    <header>
        <div class="header-title-container">
            <h1 class="header-title" title="{title}">{title}</h1>
            <div class="header-meta">
                <span>Duration: {total_duration} mins</span>
                {f' • <span>By {authors}</span>' if authors else ''}
                {f' • <span>Updated: {last_updated}</span>' if last_updated else ''}
            </div>
        </div>
        <div class="header-actions">
            <button class="btn" id="theme-toggle" onclick="toggleTheme()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" id="sun-icon" style="display: none;"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" id="moon-icon"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                Toggle Dark Mode
            </button>
            {f'<a href="{source_url}" target="_blank" class="btn btn-primary">View Original</a>' if source_url else ''}
        </div>
    </header>

    <div class="app-container">
        <aside class="sidebar">
            <h3 class="sidebar-title">Steps</h3>
            {sidebar_items}
        </aside>
        
        <main class="content-panel">
            {steps_html}
        </main>
    </div>

    <script>
        function toggleTheme() {{
            const body = document.body;
            const sunIcon = document.getElementById('sun-icon');
            const moonIcon = document.getElementById('moon-icon');
            
            body.classList.toggle('dark-mode');
            
            if (body.classList.contains('dark-mode')) {{
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'block';
                localStorage.setItem('theme', 'dark');
            }} else {{
                sunIcon.style.display = 'block';
                moonIcon.style.display = 'none';
                localStorage.setItem('theme', 'light');
            }}
        }}

        // Restore theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        if (savedTheme === 'light') {{
            document.body.classList.remove('dark-mode');
            document.getElementById('sun-icon').style.display = 'block';
            document.getElementById('moon-icon').style.display = 'none';
        }}

        // Sidebar active link highlighting on scroll
        const sections = document.querySelectorAll('.codelab-step');
        const navLinks = document.querySelectorAll('.sidebar-link');

        window.addEventListener('scroll', () => {{
            let current = "";
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                if (pageYOffset >= sectionTop - 120) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === `#` + current) {{
                    link.classList.add('active');
                }}
            }});
        }});
    </script>
</body>
</html>
"""
        return html_template

    @staticmethod
    def to_markdown(data):
        """
        Generates a clean Markdown file content by joining all steps
        separated by markdown dividers and headers.
        """
        title = data.get("title", "Codelab")
        authors = data.get("authors", "")
        last_updated = data.get("last_updated", "")
        total_duration = data.get("total_duration", 0)
        source_url = data.get("source_url", "")
        
        md_content = f"# {title}\n\n"
        if authors or last_updated or total_duration:
            md_content += "**Metadata:**\n"
            if total_duration:
                md_content += f"- **Total Duration:** {total_duration} minutes\n"
            if authors:
                md_content += f"- **Authors:** {authors}\n"
            if last_updated:
                md_content += f"- **Last Updated:** {last_updated}\n"
            if source_url:
                md_content += f"- **Source URL:** [{source_url}]({source_url})\n"
            md_content += "\n---\n\n"
            
        for step in data.get("steps", []):
            idx = step["index"]
            step_title = step["title"]
            duration = step["duration"]
            content_md = step["content_md"]
            
            md_content += f"## {idx + 1}. {step_title}\n"
            md_content += f"*Duration: {duration} mins*\n\n"
            md_content += f"{content_md}\n\n"
            md_content += "---\n\n"
            
        # Clean trailing divider
        if md_content.endswith("---\n\n"):
            md_content = md_content[:-7]
            
        return md_content

    @staticmethod
    def to_pdf(data, output_filepath):
        """
        Generates a PDF using fpdf2 by translating metadata and cleaned html
        elements of each step to PDF draw and multi-cell write operations.
        """
        # Create FPDF Instance with customized Header and Footer
        class CodelabPDF(FPDF):
            def __init__(self, codelab_title):
                super().__init__()
                self.codelab_title = codelab_title
                self.set_auto_page_break(auto=True, margin=15)
                
            def header(self):
                # Only print header if not on cover page
                if self.page_no() > 1:
                    self.set_font('helvetica', 'I', 8)
                    self.set_text_color(100, 110, 120)
                    self.cell(0, 10, self.codelab_title, 0, 0, 'R')
                    self.ln(8)
                    # Draw top thin rule
                    self.set_draw_color(226, 232, 240)
                    self.set_line_width(0.5)
                    self.line(self.get_x(), self.get_y(), 210 - self.get_x(), self.get_y())
                    self.ln(6)

            def footer(self):
                if self.page_no() > 1:
                    self.set_y(-15)
                    self.set_font('helvetica', 'I', 8)
                    self.set_text_color(100, 110, 120)
                    self.cell(0, 10, f'Page {self.page_no()} of {{nb}}', 0, 0, 'R')

        title = CodelabFormatter.sanitize_text(data.get("title", "Codelab"))
        authors = CodelabFormatter.sanitize_text(data.get("authors", ""))
        last_updated = CodelabFormatter.sanitize_text(data.get("last_updated", ""))
        total_duration = data.get("total_duration", 0)
        source_url = CodelabFormatter.sanitize_text(data.get("source_url", ""))
        
        pdf = CodelabPDF(title)
        pdf.alias_nb_pages()
        
        # --- 1. COVER PAGE ---
        pdf.add_page()
        
        # Draw a beautiful banner
        pdf.set_fill_color(26, 115, 232) # Google Primary Blue
        pdf.rect(0, 0, 210, 80, 'F')
        
        pdf.set_y(30)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.multi_cell(0, 10, title, 0, "C")
        
        pdf.set_y(95)
        pdf.set_text_color(30, 41, 59) # Slate Dark
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "Google Codelab Document", 0, 1, "C")
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 10)
        if total_duration:
            pdf.cell(0, 6, f"Estimated Reading Time: {total_duration} mins", 0, 1, "C")
        if authors:
            pdf.cell(0, 6, f"Authors: {authors}", 0, 1, "C")
        if last_updated:
            pdf.cell(0, 6, f"Last Updated: {last_updated}", 0, 1, "C")
        if source_url:
            pdf.ln(5)
            pdf.set_font("helvetica", "I", 8)
            pdf.set_text_color(26, 115, 232)
            pdf.cell(0, 6, f"Source: {source_url}", 0, 1, "C", link=source_url)
            
        pdf.set_text_color(30, 41, 59)
        
        # --- 2. RENDER STEPS ---
        for step in data.get("steps", []):
            pdf.add_page()
            idx = step["index"]
            step_title = CodelabFormatter.sanitize_text(step["title"])
            duration = step["duration"]
            content_html = step["content_html"]
            
            # Step Heading
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(26, 115, 232)
            pdf.multi_cell(0, 8, f"{idx + 1}. {step_title}")
            
            # Duration Badge/Text
            pdf.set_font("helvetica", "I", 9)
            pdf.set_text_color(100, 110, 120)
            pdf.cell(0, 6, f"Estimated time: {duration} minutes", 0, 1)
            pdf.ln(4)
            
            # Draw step header separator
            pdf.set_draw_color(26, 115, 232)
            pdf.set_line_width(1.5)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 40, pdf.get_y())
            pdf.ln(6)
            
            # Reset colors
            pdf.set_text_color(30, 41, 59)
            
            # Parse step HTML elements and write them
            soup = BeautifulSoup(content_html, 'html.parser')
            CodelabFormatter._render_html_to_pdf(pdf, soup)

        # Ensure output folder exists
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        pdf.output(output_filepath)
        return output_filepath

    @staticmethod
    def _render_html_to_pdf(pdf, soup):
        """
        Traverses top-level elements of HTML and draws them using FPDF methods.
        """
        for element in soup.children:
            if element.name is None: # Text nodes outside elements
                text = CodelabFormatter.sanitize_text(element.string.strip()) if element.string else ""
                if text:
                    pdf.set_font("helvetica", "", 10)
                    pdf.multi_cell(0, 5, text)
                    pdf.ln(3)
                continue
                
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Heading styling
                size = 14 if element.name == 'h1' or element.name == 'h2' else 12
                pdf.set_font("helvetica", "B", size)
                pdf.set_text_color(26, 115, 232)
                pdf.ln(2)
                pdf.multi_cell(0, 6, CodelabFormatter.sanitize_text(element.get_text().strip()))
                pdf.ln(3)
                pdf.set_text_color(30, 41, 59) # Reset color
                
            elif element.name == 'p':
                pdf.set_font("helvetica", "", 10)
                # Parse inline text for simple bold, italic, links
                CodelabFormatter._render_inline_text(pdf, element)
                pdf.ln(3)
                
            elif element.name == 'div' and 'callout' in element.get('class', []):
                # Callout block
                classes = element.get('class', [])
                is_warning = 'callout-warning' in classes
                
                # Colors
                bg_color = (252, 232, 230) if is_warning else (232, 240, 254)
                border_color = (217, 48, 37) if is_warning else (26, 115, 232)
                text_color = (165, 29, 36) if is_warning else (24, 90, 188)
                
                # Cache position
                start_x = pdf.get_x()
                start_y = pdf.get_y()
                
                pdf.set_font("helvetica", "", 9.5)
                pdf.set_text_color(*text_color)
                
                # Get callout text
                text_content = CodelabFormatter.sanitize_text(element.get_text().strip())
                
                # We calculate box height approximately based on text size (A4 width - margins)
                # Available width = 210 - 20 (margins) - 10 (callout padding) = 180
                # Using a dummy multi_cell print to find height if FPDF supported it, 
                # or just calculating lines:
                lines = max(1, len(text_content) // 90 + 1)
                box_height = lines * 5 + 6 # padding
                
                # Draw fill rectangle
                pdf.set_fill_color(*bg_color)
                pdf.rect(start_x, start_y, 190, box_height, 'F')
                
                # Draw left border
                pdf.set_fill_color(*border_color)
                pdf.rect(start_x, start_y, 4, box_height, 'F')
                
                # Draw text inside
                pdf.set_x(start_x + 8)
                pdf.set_y(start_y + 3)
                pdf.multi_cell(180, 5, text_content)
                
                # Reset y to bottom of the callout
                pdf.set_y(start_y + box_height)
                pdf.ln(4)
                pdf.set_text_color(30, 41, 59) # Reset slate color
                
            elif element.name == 'pre':
                # Code blocks
                code_text = CodelabFormatter.sanitize_text(element.get_text().strip())
                pdf.set_font("courier", "", 9)
                pdf.set_fill_color(246, 248, 250) # Light grey code bg
                pdf.set_draw_color(225, 228, 232)
                pdf.set_line_width(0.2)
                
                # Calculate height
                lines_count = max(1, len(code_text.split('\n')))
                box_height = lines_count * 4.5 + 6
                
                # Check for page break safety
                if pdf.get_y() + box_height > 270:
                    pdf.add_page()
                    
                start_x = pdf.get_x()
                start_y = pdf.get_y()
                
                # Draw box
                pdf.rect(start_x, start_y, 190, box_height, 'FD')
                
                # Print code text
                pdf.set_x(start_x + 5)
                pdf.set_y(start_y + 3)
                pdf.multi_cell(180, 4.5, code_text)
                
                pdf.set_y(start_y + box_height)
                pdf.ln(4)
                
            elif element.name in ['ul', 'ol']:
                pdf.set_font("helvetica", "", 10)
                bullet_num = 1
                for li in element.find_all('li', recursive=False):
                    bullet = f"{bullet_num}. " if element.name == 'ol' else "-  "
                    
                    # Store current X
                    cur_x = pdf.get_x()
                    
                    pdf.cell(10, 5, bullet, 0, 0)
                    
                    # Print list item text
                    # We wrap item text in 180mm width
                    pdf.multi_cell(180, 5, CodelabFormatter.sanitize_text(li.get_text().strip()))
                    pdf.set_x(cur_x)
                    
                    bullet_num += 1
                pdf.ln(3)
                
            elif element.name == 'img':
                src = element.get('src')
                if src:
                    try:
                        # Fetch image
                        resp = requests.get(src, timeout=10)
                        if resp.status_code == 200:
                            img_data = io.BytesIO(resp.content)
                            pil_img = Image.open(img_data)
                            
                            # Convert RGBA to RGB to avoid FPDF conversion issues
                            if pil_img.mode in ('RGBA', 'LA') or (pil_img.mode == 'P' and 'transparency' in pil_img.info):
                                background = Image.new("RGB", pil_img.size, (255, 255, 255))
                                background.paste(pil_img, mask=pil_img.split()[3] if pil_img.mode == 'RGBA' else None)
                                pil_img = background
                            
                            # Calculate dimensions (keeping aspect ratio, fitting max width 170mm)
                            width, height = pil_img.size
                            pdf_width = min(170.0, float(width) * 0.264583) # pixels to mm approx
                            pdf_height = (pdf_width / width) * height
                            
                            # Page break check
                            if pdf.get_y() + pdf_height > 275:
                                pdf.add_page()
                                
                            # Center image
                            center_x = (210 - pdf_width) / 2
                            
                            # Add to PDF
                            pdf.image(pil_img, x=center_x, w=pdf_width, h=pdf_height)
                            pdf.ln(4)
                    except Exception as e:
                        # Fallback if image fetching/conversion fails
                        pdf.set_font("helvetica", "I", 9)
                        pdf.set_text_color(100, 110, 120)
                        pdf.cell(0, 5, f"[Failed to load image: {src}]", 0, 1)
                        pdf.ln(3)
                        pdf.set_text_color(30, 41, 59)

    @staticmethod
    def _render_inline_text(pdf, paragraph_element):
        """
        Simple inline HTML parser for styling: bold <b>/<strong>, 
        italic <i>/<em>, and links <a>.
        """
        # Since FPDF multi_cell doesn't easily support mixed formatting in a single cell,
        # we do a simple sequential draw of text chunks if possible, or fall back to plain text
        # for complex cases, or use basic HTML parser write if safe.
        # But reportlab/fpdf2 has write_html. Can we use fpdf2's write_html for the paragraph?
        # Yes! FPDF has a pdf.write_html() method which is perfect for rendering inline text
        # in a paragraph! We will wrap the paragraph element back to string and use write_html.
        try:
            # We must escape curly brackets because write_html has some issues otherwise,
            # and format links/tags cleanly.
            p_html = CodelabFormatter.sanitize_text(str(paragraph_element))
            
            # Clean up classes or invalid attributes from <p> tag to prevent FPDF parser crashes
            p_html = re.sub(r'<p[^>]*>', '<p>', p_html)
            p_html = re.sub(r'<span[^>]*>', '', p_html)
            p_html = p_html.replace('</span>', '')
            
            # Use write_html for paragraphs
            pdf.write_html(p_html)
            # FPDF write_html doesn't automatically insert a new line after paragraph, so we add a tiny space
            pdf.ln(1)
        except Exception:
            # Fallback to plain text if write_html fails
            pdf.multi_cell(0, 5, CodelabFormatter.sanitize_text(paragraph_element.get_text().strip()))
