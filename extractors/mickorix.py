import os
import re
from . import BaseExtractor

class MickorixExtractor(BaseExtractor):
    def extract(self):
        base_dir = "awesome-nanobanana-images-mickorix"
        readme_path = os.path.join(base_dir, "README.md")
        if os.path.exists(os.path.join(base_dir, "README_en.md")):
            readme_path = os.path.join(base_dir, "README_en.md")
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()

        # Logic for Mickorix:
        # ### 例 X: [Title](link) (by [@Author](link))
        # Content: Tables with inputs/outputs. **提示词:** code block.
        
        # Regex to capture sections
        # Match "### 例 X: Title (by @Author)" where Title can be Linked or Text, and parens can be full/half width.
        # Added capturing group for author URL
        case_pattern = re.compile(r'### (?:Case|Example|例) (\d+): (.*?)[（\(]by \[@(.*?)\]\((.*?)\)[）\)](.*?)(?=### (?:Case|Example|例)|\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            case_id = match.group(1)
            raw_title = match.group(2).strip()
            author = match.group(3)
            author_url = match.group(4)
            body = match.group(5)
            
            # Clean title if it's a markdown link [Text](URL)
            title = raw_title
            original_url = ""
            
            # Updated to capture URL from title[Text](URL)
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', raw_title)
            if link_match:
                title = link_match.group(1)
                original_url = link_match.group(2)
            
            # Extract Image (Output column)
            image_url = ""
            # Often images are in local 'images/' folder. Need to prefix repo URL.
            img_match = re.search(r'<img src="(.*?)"', body)
            if img_match:
                img_path = img_match.group(1)
                image_url = f"https://github.com/Mickorix/awesome-nanobanana-images/raw/main/{img_path}"

            # Extract Prompt
            prompt = ""
            code_match = re.search(r'```(?:text|json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
            
            description = f"Example {case_id}: {title}"
            
            metadata = {
                "title": title,
                "author": author,
                "author_url": author_url,
                "original_url": original_url,
                "repo_url": "https://github.com/Mickorix/awesome-nanobanana-images",
                "image_url": image_url,
                "tags": ["mickorix", f"case-{case_id}"]
            }
            
            self.save_entry(metadata, description, prompt, f"mickorix-{case_id}-{title}", subdir="mickorix")
            count += 1
            
        return count
