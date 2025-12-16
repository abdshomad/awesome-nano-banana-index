"""Indexer module for extracting and indexing content from submodules."""

import yaml
from pathlib import Path
from typing import List, Dict, Optional
from .config import SUBMODULES_DIR, GITMODULES_FILE, BASE_DIR
from .utils import (
    parse_gitmodules,
    extract_markdown_text,
    generate_document_id,
    determine_language
)


def scan_submodules() -> List[Dict]:
    """Scan and return list of submodules from .gitmodules."""
    return parse_gitmodules(GITMODULES_FILE)


def extract_case_data(case_path: Path, submodule_name: str) -> Optional[Dict]:
    """Extract case data from case.yml and ATTRIBUTION.yml files."""
    case_file = case_path / "case.yml"
    attribution_file = case_path / "ATTRIBUTION.yml"
    
    if not case_file.exists():
        return None
    
    try:
        # Load case.yml
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = yaml.safe_load(f) or {}
        
        # Load ATTRIBUTION.yml if it exists
        attribution_data = {}
        if attribution_file.exists():
            with open(attribution_file, "r", encoding="utf-8") as f:
                attribution_data = yaml.safe_load(f) or {}
        
        # Extract image file
        image_file = None
        image_name = case_data.get("image", "")
        if image_name:
            image_path = case_path / image_name
            if image_path.exists():
                image_file = str(image_path.relative_to(BASE_DIR))
        
        # Build document
        doc_id = generate_document_id(
            submodule_name,
            "case",
            str(case_path.relative_to(BASE_DIR))
        )
        
        # Determine language
        title = case_data.get("title", "")
        title_en = case_data.get("title_en", "")
        language = determine_language(title, title_en)
        
        # Build content string for full-text search
        content_parts = [
            case_data.get("title", ""),
            case_data.get("title_en", ""),
            case_data.get("prompt", ""),
            case_data.get("prompt_en", ""),
            case_data.get("alt_text", ""),
            case_data.get("alt_text_en", ""),
            case_data.get("prompt_note", ""),
            case_data.get("prompt_note_en", ""),
            case_data.get("reference_note", ""),
            case_data.get("reference_note_en", ""),
        ]
        content = " ".join(filter(None, content_parts))
        
        document = {
            "id": doc_id,
            "type": "case",
            "submodule": submodule_name,
            "path": str(case_path.relative_to(BASE_DIR)),
            "title": title or "",
            "title_en": title_en or "",
            "prompt": case_data.get("prompt", "") or "",
            "prompt_en": case_data.get("prompt_en", "") or "",
            "author": case_data.get("author", "") or attribution_data.get("prompt_author", "") or "",
            "author_link": case_data.get("author_link", "") or attribution_data.get("prompt_author_link", "") or "",
            "image": image_file or "",
            "capability_code": case_data.get("capability_code", "") or "",
            "capability_type": case_data.get("capability_type", "") or "",
            "content": content,
            "language": language,
            "source_links": case_data.get("source_links", []) or [],
        }
        
        return document
        
    except Exception as e:
        print(f"Error extracting case data from {case_path}: {e}")
        return None


def extract_markdown_content(md_path: Path, submodule_name: str) -> Optional[Dict]:
    """Extract content from markdown file."""
    if not md_path.exists():
        return None
    
    try:
        content = extract_markdown_text(md_path)
        
        if not content:
            return None
        
        doc_id = generate_document_id(
            submodule_name,
            "readme" if md_path.name.lower() == "readme.md" else "documentation",
            str(md_path.relative_to(BASE_DIR))
        )
        
        # Try to extract title from first heading
        title = ""
        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
        
        document = {
            "id": doc_id,
            "type": "readme" if md_path.name.lower() == "readme.md" else "documentation",
            "submodule": submodule_name,
            "path": str(md_path.relative_to(BASE_DIR)),
            "title": title,
            "title_en": title,
            "prompt": "",
            "prompt_en": "",
            "author": "",
            "author_link": "",
            "image": "",
            "capability_code": "",
            "capability_type": "",
            "content": content,
            "language": "en",  # Default to English for markdown
            "source_links": [],
        }
        
        return document
        
    except Exception as e:
        print(f"Error extracting markdown from {md_path}: {e}")
        return None


def build_index(rebuild: bool = False) -> List[Dict]:
    """Build index by scanning all submodules and extracting content."""
    documents = []
    submodules = scan_submodules()
    
    print(f"Found {len(submodules)} submodules")
    
    for submodule in submodules:
        submodule_name = submodule.get("name", "")
        submodule_path = submodule.get("path", "")
        
        if not submodule_path:
            continue
        
        full_path = BASE_DIR / submodule_path
        
        if not full_path.exists():
            print(f"Submodule path does not exist: {full_path}")
            continue
        
        print(f"Processing submodule: {submodule_name}")
        
        # Process cases directory if it exists
        cases_dir = full_path / "cases"
        if cases_dir.exists() and cases_dir.is_dir():
            case_dirs = [d for d in cases_dir.iterdir() if d.is_dir() and d.name.isdigit()]
            
            for case_dir in case_dirs:
                case_doc = extract_case_data(case_dir, submodule_name)
                if case_doc:
                    documents.append(case_doc)
        
        # Process README files
        readme_files = [
            full_path / "README.md",
            full_path / "README_en.md",
            full_path / "README_zh.md",
        ]
        
        for readme_file in readme_files:
            if readme_file.exists():
                md_doc = extract_markdown_content(readme_file, submodule_name)
                if md_doc:
                    documents.append(md_doc)
        
        # Process other markdown files in root
        for md_file in full_path.glob("*.md"):
            if md_file.name.lower() not in ["readme.md", "readme_en.md", "readme_zh.md"]:
                md_doc = extract_markdown_content(md_file, submodule_name)
                if md_doc:
                    documents.append(md_doc)
    
    print(f"Extracted {len(documents)} documents")
    return documents
