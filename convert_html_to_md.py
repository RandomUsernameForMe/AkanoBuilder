import os
import re
from html.parser import HTMLParser

INPUT_DIR = "inputs"

class GDocToMarkdown(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown_lines = []
        self.list_depth = 0
        self.in_title = False
        self.current_tag = None
        self.ignore_content = False

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in ['head', 'style', 'script']:
            self.ignore_content = True
            return

        if tag == 'h1':
            self.markdown_lines.append('\n\n## ') # Google Doc H1 -> Markdown H2
        elif tag == 'h2':
            self.markdown_lines.append('\n\n### ') # Google Doc H2 -> Markdown H3
        elif tag == 'h3':
            self.markdown_lines.append('\n\n#### ')
        elif tag in ['ul', 'ol']:
            self.list_depth += 1
        elif tag == 'li':
            self.markdown_lines.append('\n' + '  ' * (self.list_depth - 1) + '- ')
        elif tag == 'p':
            # Check if it's a title class (Google Docs Title -> Markdown H1)
            is_title = False
            for k, v in attrs:
                if k == 'class' and 'title' in v:
                    is_title = True
                    break
            
            if is_title:
                self.markdown_lines.append('\n# ')
                self.in_title = True
            else:
                self.markdown_lines.append('\n\n')
        elif tag == 'br':
            self.markdown_lines.append('\n')

    def handle_endtag(self, tag):
        if tag in ['head', 'style', 'script']:
            self.ignore_content = False
            return

        if tag in ['ul', 'ol']:
            self.list_depth -= 1
        elif tag == 'p':
            if self.in_title:
                self.markdown_lines.append('\n')
                self.in_title = False
        self.current_tag = None

    def handle_data(self, data):
        if self.ignore_content:
            return

        text = data.strip()
        if text:
            # Simple escape for markdown special chars if needed, but usually raw text is fine
            self.markdown_lines.append(text)

    def get_markdown(self):
        # Join and clean up excessive newlines
        content = "".join(self.markdown_lines)
        return re.sub(r'\n{3,}', '\n\n', content).strip()

def convert_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple check if file is HTML
    if "<html" not in content.lower() and "<!doctype html>" not in content.lower():
        return

    print(f"Converting {filepath} from HTML to Markdown...", end=" ")
    parser = GDocToMarkdown()
    parser.feed(content)
    md_content = parser.get_markdown()

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Done.")

if __name__ == "__main__":
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            convert_file(os.path.join(INPUT_DIR, filename))