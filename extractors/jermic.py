import os
import re
from . import BaseExtractor

class JermicExtractor(BaseExtractor):
    def extract(self):
        base_dir = "awesome-aiart-pics-prompts-Jermic"
        readme_path = os.path.join(base_dir, "README.md")
        if os.path.exists(os.path.join(base_dir, "README_EN.md")):
            readme_path = os.path.join(base_dir, "README_EN.md")
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()

        # Logic for Jermic:
        # Structure sections: ## Author Name
        # Sub-sections: ### [Title](link)
        # Content: **作者**: [@Name](link) ... **来源**: [X](link) ... <img src="..."> ... ```prompt```
        
        # Split by "---" separator which seems common in this file
        sections = content.split('---')
        
        for section in sections:
            # Check if this valid section with a case
            if "### [" not in section:
                continue
            
            try:
                # Extract Title
                title_match = re.search(r'### \[(.*?)\]\(.*?\)', section)
                title = title_match.group(1) if title_match else "Unknown Title"
                
                # Extract Author from line like **作者**: [@Name](link) or **Author**:
                author_match = re.search(r'\*\*(?:作者|Author)\*\*: \[@(.*?)\]', section, re.IGNORECASE)
                author = author_match.group(1) if author_match else "Unknown Author"
                
                # Extract Source
                source_match = re.search(r'\*\*(?:来源|Source)\*\*: \[(.*?)\]\((.*?)\)', section, re.IGNORECASE)
                source_url = source_match.group(2) if source_match else ""
                
                # Extract Image
                img_match = re.search(r'<img src="(.*?)"', section)
                image_url = img_match.group(1) if img_match else ""
                
                # Extract Prompt
                # Look for code block
                prompt = ""
                code_match = re.search(r'```(?:json)?\n(.*?)\n```', section, re.DOTALL)
                if code_match:
                    prompt = code_match.group(1)
                
                if not prompt:
                    continue

                description = f"Collection from Awesome AI Art Pics Prompts by {author}"
                
                metadata = {
                    "title": title,
                    "author": author,
                    "repo_url": source_url or "https://github.com/Jermic/awesome-aiart-pics-prompts",
                    "image_url": image_url,
                    "tags": ["jermic", "aiart"]
                }
                
                # Use title for filename but clean it
                self.save_entry(metadata, description, prompt, f"jermic-{title}", subdir="jermic")
                count += 1
                
            except Exception as e:
                print(f"Skipping section due to error: {e}")
                continue
            
        return count
