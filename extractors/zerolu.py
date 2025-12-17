import os
import re
from . import BaseExtractor

class ZeroLuExtractor(BaseExtractor):
    def extract(self):
        readme_path = "awesome-nanobanana-pro-ZeroLu/README.md"
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()

        # Logic for ZeroLu:
        # ### 1.1. Title
        # **Prompt:** ... ```code```
        
        # Regex to capture sections
        # Pattern: ### \d+\.\d+\. (.*?)\n(.*?)(?=### |\Z)
        
        case_pattern = re.compile(r'### \d+\.\d+\. (.*?)\n(.*?)(?=### |\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            title = match.group(1).strip()
            body = match.group(2)
            
            # Extract Image
            image_url = ""
            img_match = re.search(r'<img .*?src="(.*?)"', body)
            if img_match:
                img_path = img_match.group(1)
                if not img_path.startswith("http"):
                     image_url = f"https://github.com/ZeroLu/awesome-nanobanana-pro/raw/main/{img_path}"
                else:
                    image_url = img_path

            # Extract Prompt
            prompt = ""
            code_match = re.search(r'```(?:text|json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
            
            # Extract Source/Author
            author = "ZeroLu Collection"
            source_match = re.search(r'\*Source: \[@(.*?)\]\(.*?\)\*', body)
            if source_match:
                author = source_match.group(1)
            
            description = f"Case: {title}"
            
            metadata = {
                "title": title,
                "author": author,
                "repo_url": "https://github.com/ZeroLu/awesome-nanobanana-pro",
                "image_url": image_url,
                "tags": ["zerolu"]
            }
            
            self.save_entry(metadata, description, prompt, f"zerolu-{title}", subdir="zerolu")
            count += 1
            
        return count

class MurattasdemirExtractor(BaseExtractor):
    def extract(self):
        readme_path = "awesome-nanobanana-pro-murattasdemir/README.md"
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()
            
        # Logic is very similar to ZeroLu
        case_pattern = re.compile(r'### \d+\.\d+\. (.*?)\n(.*?)(?=### |\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            title = match.group(1).strip()
            body = match.group(2)
            
            image_url = ""
            img_match = re.search(r'<img .*?src="(.*?)"', body)
            if img_match:
                img_path = img_match.group(1)
                if not img_path.startswith("http"):
                     image_url = f"https://github.com/murattasdemir/awesome-nanobanana-pro/raw/main/{img_path}"
                else:
                    image_url = img_path

            prompt = ""
            code_match = re.search(r'```(?:text|json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
            
            author = "Murattasdemir Collection"
            source_match = re.search(r'\*Source: \[@(.*?)\]\(.*?\)\*', body)
            if source_match:
                author = source_match.group(1)
            
            description = f"Case: {title}"
            
            metadata = {
                "title": title,
                "author": author,
                "repo_url": "https://github.com/murattasdemir/awesome-nanobanana-pro",
                "image_url": image_url,
                "tags": ["murattasdemir"]
            }
            
            self.save_entry(metadata, description, prompt, f"murattasdemir-{title}", subdir="murattasdemir")
            count += 1
            
        return count
