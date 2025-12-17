import os
import re
import yaml
import glob
import json
from . import BaseExtractor

class SuperMakerExtractor(BaseExtractor):
    def extract(self):
        repo_path = "awesome-nano-banana-Super-Maker-AI"
        readme_path = os.path.join(repo_path, "README.md")
        if not os.path.exists(readme_path):
            return 0
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find cases
        case_pattern = r'### Case \d+: (.*?) \(by (.*?)\)'
        
        matches = list(re.finditer(case_pattern, content))
        count = 0
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            author = match.group(2).strip()
            
            start_idx = match.end()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
            
            section_content = content[start_idx:end_idx]
            
            # Extract prompt from yaml block
            prompt_match = re.search(r'```yaml\n(.*?)\n```', section_content, re.DOTALL)
            if prompt_match:
                prompt_text = prompt_match.group(1).strip()
                
                # Extract image url if possible for metadata
                img_match = re.search(r'!\[.*?\]\((.*?)\)', section_content)
                image_url = ""
                if img_match:
                    relative_url = img_match.group(1)
                    if relative_url.startswith('http'):
                        image_url = relative_url
                    else:
                        # Construct raw github url if possible, or just keep relative?
                        # Let's keep relative for now or construct based on repo structure
                        image_url = relative_url
                
                metadata = {
                    "title": title,
                    "author": author,
                    "repo_url": "https://github.com/SuperMaker-AI/awesome-nano-banana-Super-Maker-AI",
                    "image_url": image_url,
                    "tags": ["SuperMaker"]
                }
                
                self.save_entry(metadata, description="", prompt=prompt_text, filename_hint=title, subdir="super_maker")
                count += 1
                
        return count

class MusetExtractor(BaseExtractor):
    def extract(self):
        cases_dir = "awesome-nano-banana-pro-muset-ai/cases"
        case_files = glob.glob(os.path.join(cases_dir, "*", "case.yml"))
        
        count = 0
        for case_file in case_files:
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    case_data = yaml.safe_load(f)
                    
                dir_path = os.path.dirname(case_file)
                attr_file = os.path.join(dir_path, "ATTRIBUTION.yml")
                
                author = "Unknown"
                if os.path.exists(attr_file):
                    with open(attr_file, 'r', encoding='utf-8') as f:
                        attr_data = yaml.safe_load(f)
                        if attr_data:
                            author = attr_data.get('prompt_author', 'Unknown')
                
                title = case_data.get('title', 'Untitled')
                prompt = case_data.get('prompt', '')
                
                if isinstance(prompt, str):
                    metadata = {
                        "title": title,
                        "author": author,
                        "repo_url": "https://github.com/muset-ai/awesome-nano-banana-pro-muset-ai",
                        "tags": ["MusetAI"]
                    }
                    self.save_entry(metadata, description="", prompt=prompt.strip(), filename_hint=title, subdir="muset_ai")
                    count += 1
            except Exception:
                continue
                
        return count

class YouMindExtractor(BaseExtractor):
    def extract(self):
        repo_path = "awesome-nano-banana-pro-prompts-YouMind-OpenLab"
        readme_path = os.path.join(repo_path, "README.md")
        if not os.path.exists(readme_path):
            return 0
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = list(re.finditer(r'### No\. \d+: (.*)', content))
        count = 0
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            
            start_idx = match.end()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
            section = content[start_idx:end_idx]
            
            author_match = re.search(r'\*\*Author:\*\* \[(.*?)\]', section)
            author = author_match.group(1) if author_match else "YouMind"
            
            # Match prompt block
            prompt_section_match = re.search(r'#### 📝 Prompt\s*\n\s*```.*?\n(.*?)\n```', section, re.DOTALL)
            
            if prompt_section_match:
                prompt_text = prompt_section_match.group(1).strip()
                
                metadata = {
                    "title": title,
                    "author": author,
                    "repo_url": "https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts",
                    "tags": ["YouMind"]
                }
                
                self.save_entry(metadata, description="", prompt=prompt_text, filename_hint=title, subdir="youmind")
                count += 1
                
        return count
