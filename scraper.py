import urllib.parse
import requests
from bs4 import BeautifulSoup

class CodelabScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape(self, url):
        """
        Scrapes a Google Codelab URL and returns structured data containing
        metadata and steps with cleaned HTML and Markdown content.
        """
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Parse main codelab tag and metadata
        codelab_tag = soup.find('google-codelab')
        if not codelab_tag:
            # Fallback if the google-codelab tag is missing but page structure has steps
            codelab_title = soup.find('h1', class_='devsite-page-title')
            codelab_title = codelab_title.text.strip() if codelab_title else "Scraped Codelab"
            codelab_id = "codelab"
        else:
            codelab_title = codelab_tag.get('title', 'Scraped Codelab')
            codelab_id = codelab_tag.get('id', 'codelab')

        # Extract about metadata (author, last updated, etc.)
        about_tag = soup.find('google-codelab-about')
        authors = ""
        last_updated = ""
        if about_tag:
            authors = about_tag.get('authors', '')
            last_updated = about_tag.get('last-updated', '')

        # 2. Extract steps
        step_tags = soup.find_all('google-codelab-step')
        if not step_tags:
            # Fallback if steps are represented by standard sections
            step_tags = soup.find_all('section')

        steps = []
        for index, step_tag in enumerate(step_tags):
            step_title = step_tag.get('label', f"Step {index + 1}")
            step_duration = step_tag.get('duration', '0')
            
            # Clone content to avoid mutating original soup
            import copy
            content_node = copy.copy(step_tag)
            
            # Clean up metadata or analytics inside the step
            for tag in content_node.find_all(['google-codelab-about', 'google-codelab-analytics', 'devsite-actions']):
                tag.decompose()
                
            # Process and clean standard elements
            self._clean_elements(content_node, url, soup)
            
            # Extract HTML
            # We want the inner HTML of the step, so we join the string representations of all children
            content_html = "".join(str(child) for child in content_node.children).strip()
            
            # Generate Markdown
            content_md = self._html_to_markdown(content_node)
            
            steps.append({
                "index": index,
                "title": step_title,
                "duration": step_duration,
                "content_html": content_html,
                "content_md": content_md
            })
            
        total_duration = sum(int(s['duration']) for s in steps if s['duration'].isdigit())
        
        return {
            "id": codelab_id,
            "title": codelab_title,
            "authors": authors,
            "last_updated": last_updated,
            "total_duration": total_duration,
            "steps": steps,
            "source_url": url
        }

    def _clean_elements(self, soup_node, base_url, main_soup):
        """
        Cleans custom elements in soup_node:
        - Resolves images and links to absolute URLs.
        - Translates custom aside notes/warnings to standard HTML divs.
        - Translates devsite code snippets to standard pre/code.
        """
        # Resolve images
        for img in soup_node.find_all('img'):
            if img.get('src'):
                img['src'] = urllib.parse.urljoin(base_url, img['src'])
            if img.get('srcset'):
                del img['srcset']
            # Clean up style attributes that might break rendering
            if img.get('style'):
                img['style'] = "max-width: 100%; height: auto; display: block; margin: 1.5rem auto; border-radius: 8px;"
            else:
                img['style'] = "max-width: 100%; height: auto; display: block; margin: 1.5rem auto; border-radius: 8px;"

        # Resolve links
        for a in soup_node.find_all('a'):
            if a.get('href'):
                a['href'] = urllib.parse.urljoin(base_url, a['href'])
                a['target'] = "_blank"

        # Convert <aside> or boxes to clean styled callout divs
        for aside in soup_node.find_all(['aside', 'div'], class_=['special', 'warning']):
            classes = aside.get('class', [])
            aside.name = 'div'
            aside_type = 'warning' if 'warning' in classes else 'note'
            aside['class'] = f"callout callout-{aside_type}"
            # Inject a label only if not already present
            label = "Warning" if aside_type == 'warning' else "Note"
            text_content = aside.get_text().strip().lower()
            if not text_content.startswith(label.lower()):
                label_tag = main_soup.new_tag('strong')
                label_tag.string = f"{label}: "
                if aside.contents:
                    # Find the first paragraph or insert at the start
                    first_p = aside.find('p')
                    if first_p:
                        first_p.insert(0, label_tag)
                    else:
                        aside.insert(0, label_tag)
            # Remove original classes to prevent conflicts
            aside['style'] = self._get_callout_style(aside_type)

        # Convert <devsite-code> or custom pre blocks to standard pre + code
        for code_container in soup_node.find_all('devsite-code'):
            pre_tag = code_container.find('pre')
            if pre_tag:
                code_tag = pre_tag.find('code')
                lang = ""
                if code_tag and code_tag.get('language'):
                    lang = code_tag['language'].replace('language-', '')
                elif pre_tag.get('syntax'):
                    lang = pre_tag['syntax']
                
                # Create standard pre/code block
                new_pre = main_soup.new_tag('pre')
                new_pre['style'] = "background-color: #f6f8fa; padding: 1rem; border-radius: 6px; overflow-x: auto; border: 1px solid #e1e4e8; margin: 1rem 0;"
                new_code = main_soup.new_tag('code')
                if lang:
                    new_code['class'] = f"language-{lang}"
                
                # Fetch text content
                new_code.string = pre_tag.get_text()
                new_pre.append(new_code)
                code_container.replace_with(new_pre)
            else:
                code_container.decompose()

    def _get_callout_style(self, callout_type):
        """Returns standard inline styling for HTML/PDF representation of callouts."""
        if callout_type == 'warning':
            return "background-color: #fce8e6; border-left: 4px solid #d93025; padding: 1rem; border-radius: 0 4px 4px 0; margin: 1.5rem 0; color: #a51d24;"
        else: # note / special
            return "background-color: #e8f0fe; border-left: 4px solid #1a73e8; padding: 1rem; border-radius: 0 4px 4px 0; margin: 1.5rem 0; color: #185abc;"

    def _html_to_markdown(self, bs_node):
        """
        Converts a BeautifulSoup node's HTML contents to clean Markdown.
        We custom-traverse the nodes to handle lists, code blocks, bold text,
        images, and callouts cleanly.
        """
        import markdownify
        # We clean the html specifically for conversion to avoid nested/weird tags
        html_str = "".join(str(child) for child in bs_node.children).strip()
        
        # Configure markdownify
        md = markdownify.markdownify(
            html_str,
            heading_style="ATX",
            bullets="-",
            code_language_callback=lambda el: el.get('class', [''])[0].replace('language-', '') if el.get('class') else ''
        )
        return md
