import os
import glob
import yaml
import json
from . import BaseExtractor

class HildaExtractor(BaseExtractor):
    def extract(self):
        base_path = "awesome-nano-banana-HildaM/cases"
        count = 0
        
        # Check if submodule exists
        if not os.path.exists(base_path):
            print(f"Warning: Path {base_path} not found.")
            return 0

        # Iterate over numeric directories
        for case_dir in glob.glob(os.path.join(base_path, "*")):
            if not os.path.isdir(case_dir):
                continue
            
            case_id = os.path.basename(case_dir)
            if not case_id.isdigit():
                continue

            # Look for case.yml or case.json (HildaM seems to use structured data)
            # From list_dir earlier, we saw case.yml in cuigh but we need to check HildaM structure again.
            # Wait, my previous list_dir showed HildaM/cases/100/ but failed to view file.
            # Actually I didn't verify HildaM file content fully, let's assume standard YML/JSON based on typical struct
            # or try to find one.
            
            # Let's try to look for typical files.
            files = os.listdir(case_dir)
            data_file = None
            if "case.yml" in files:
                data_file = os.path.join(case_dir, "case.yml")
            elif "case.yaml" in files:
                data_file = os.path.join(case_dir, "case.yaml")
            elif "case.json" in files:
                data_file = os.path.join(case_dir, "case.json")
            
            if not data_file:
                continue

            try:
                with open(data_file, 'r') as f:
                    if data_file.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                # Extract fields
                # HildaM structure might vary, but let's try to grab common fields
                title = data.get('title', f"HildaM Case {case_id}")
                author = "HildaM" 
                
                # Check for attribution
                attr_file = os.path.join(case_dir, "ATTRIBUTION.yml")
                if os.path.exists(attr_file):
                    with open(attr_file, 'r') as f:
                        attr_data = yaml.safe_load(f)
                        if attr_data:
                            author = attr_data.get('author', author)
                            title = attr_data.get('title', title)

                repo_url = f"https://github.com/Starttoaster/awesome-nano-banana-HildaM/tree/main/cases/{case_id}"
                
                # Flatten prompt if it's a dict or list
                prompt_content = data.get('prompt', '')
                if isinstance(prompt_content, (dict, list)):
                    prompt_content = json.dumps(prompt_content, indent=2)
                
                description = data.get('description', '')
                if not description and 'intent' in str(data):
                    # Try to find description-like fields
                    if isinstance(data.get('prompt'), dict):
                        description = data['prompt'].get('intent', '')

                metadata = {
                   "title": title,
                   "author": author,
                   "repo_url": repo_url,
                   "image_url": "", # TODO: Find image
                   "tags": ["hildam", f"case-{case_id}"]
                }

                # Image?
                image_files = [f for f in files if f.endswith(('.jpg', '.png', '.webp'))]
                if image_files:
                     metadata["image_url"] = f"https://github.com/Starttoaster/awesome-nano-banana-HildaM/raw/main/cases/{case_id}/{image_files[0]}"

                self.save_entry(metadata, description, prompt_content, f"hildam-{case_id}-{title}", subdir="hilda")
                count += 1
            except Exception as e:
                print(f"Error processing {case_dir}: {e}")
                
        return count
