"""Utility functions for the search engine."""

import re
from pathlib import Path
from typing import List, Optional


def parse_gitmodules(gitmodules_path: Path) -> List[dict]:
    """Parse .gitmodules file and return list of submodule information."""
    submodules = []
    
    if not gitmodules_path.exists():
        return submodules
    
    current_submodule = {}
    
    with open(gitmodules_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            if line.startswith("[submodule"):
                if current_submodule:
                    submodules.append(current_submodule)
                # Extract submodule name from [submodule "name"]
                match = re.search(r'"([^"]+)"', line)
                current_submodule = {"name": match.group(1) if match else ""}
            elif line.startswith("path = "):
                current_submodule["path"] = line.split("=", 1)[1].strip()
            elif line.startswith("url = "):
                current_submodule["url"] = line.split("=", 1)[1].strip()
    
    if current_submodule:
        submodules.append(current_submodule)
    
    return submodules


def extract_markdown_text(md_path: Path) -> str:
    """Extract text content from markdown file."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove code blocks
        content = re.sub(r"```[\s\S]*?```", "", content)
        content = re.sub(r"`[^`]+`", "", content)
        
        # Remove links but keep text
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)
        
        # Remove images
        content = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", content)
        
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        
        # Clean up whitespace
        content = re.sub(r"\n\s*\n", "\n\n", content)
        
        return content.strip()
    except Exception as e:
        print(f"Error reading markdown file {md_path}: {e}")
        return ""


def generate_document_id(submodule: str, doc_type: str, path: str) -> str:
    """Generate a unique document ID."""
    # Create a unique ID from submodule, type, and path
    import hashlib
    combined = f"{submodule}:{doc_type}:{path}"
    return hashlib.md5(combined.encode()).hexdigest()


def determine_language(title: Optional[str], title_en: Optional[str]) -> str:
    """Determine language based on available fields."""
    has_zh = bool(title and title.strip())
    has_en = bool(title_en and title_en.strip())
    
    if has_zh and has_en:
        return "both"
    elif has_zh:
        return "zh"
    elif has_en:
        return "en"
    else:
        return "unknown"
