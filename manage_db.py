#!/usr/bin/env python3
import os
import glob
import click
import yaml
import re
import json
import http.server
import socketserver
import webbrowser
from extractors.hilda import HildaExtractor
from extractors.cuigh import CuighExtractor
from extractors.jermic import JermicExtractor
from extractors.jimmy import JimmyLvExtractor
from extractors.mickorix import MickorixExtractor
from extractors.picotrex import PicoTrexExtractor
from extractors.zerolu import ZeroLuExtractor, MurattasdemirExtractor
from extractors.new_extractors import SuperMakerExtractor, MusetExtractor, YouMindExtractor

DATABASE_DIR = "database"

def parse_frontmatter(content):
    """
    Parses YAML frontmatter from a markdown string.
    Returns (metadata_dict, content_body)
    """
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        try:
            metadata = yaml.safe_load(match.group(1))
            body = match.group(2)
            return metadata, body
        except yaml.YAMLError:
            return None, content
    return None, content

@click.group()
def cli():
    """Manage the Nano Banana text database."""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)

@cli.command()
def list():
    """List all database entries."""
    files = glob.glob(os.path.join(DATABASE_DIR, "**", "*.md"), recursive=True)
    if not files:
        click.echo("No entries found.")
        return

    click.echo(f"{'TITLE':<30} | {'AUTHOR':<20} | {'FILE':<30}")
    click.echo("-" * 86)

    for file_path in files:
        with open(file_path, 'r') as f:
            content = f.read()
            metadata, _ = parse_frontmatter(content)
            
            filename = os.path.basename(file_path)
            if metadata:
                title = metadata.get('title', 'Unknown')
                author = metadata.get('author', 'Unknown')
            else:
                title = "Invalid Format"
                author = "Unknown"
            
            # Truncate
            if len(title) > 28: title = title[:25] + "..."
            if len(author) > 18: author = author[:15] + "..."
            
            click.echo(f"{title:<30} | {author:<20} | {filename:<30}")

@cli.command()
def add():
    """Add a new entry interactively."""
    click.echo("Creating a new Nano Banana prompt entry.")
    
    title = click.prompt("Title")
    author = click.prompt("Author")
    repo_url = click.prompt("Repo URL", default="")
    image_url = click.prompt("Image URL", default="")
    tags_str = click.prompt("Tags (comma separated)", default="")
    
    description = click.prompt("Description")
    prompt_text = click.prompt("Prompt Text")
    
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    
    metadata = {
        "title": title,
        "author": author,
        "repo_url": repo_url,
        "image_url": image_url,
        "tags": tags
    }
    
    # Generate filename
    slug = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-')
    slug = re.sub(r'-+', '-', slug)
    filename = f"{slug}.md"
    filepath = os.path.join(DATABASE_DIR, filename)
    
    if os.path.exists(filepath):
        if not click.confirm(f"File {filename} exists. Overwrite?"):
            click.echo("Aborted.")
            return

    content = "---\n"
    content += yaml.dump(metadata, sort_keys=False)
    content += "---\n\n"
    content += "## Description\n"
    content += f"{description}\n\n"
    content += "## Prompt\n"
    content += f"{prompt_text}\n"
    
    with open(filepath, 'w') as f:
        f.write(content)
        
    click.echo(f"Created entry: {filepath}")

@cli.command()
def validate():
    """Validate all database entries."""
    files = glob.glob(os.path.join(DATABASE_DIR, "**", "*.md"), recursive=True)
    has_error = False
    
    for file_path in files:
        with open(file_path, 'r') as f:
            content = f.read()
            metadata, body = parse_frontmatter(content)
            
            issues = []
            if not metadata:
                issues.append("Invalid or missing frontmatter")
            else:
                required = ['title', 'author']
                for field in required:
                    if field not in metadata:
                        issues.append(f"Missing required field: {field}")
            
            if issues:
                has_error = True
                click.echo(f"FAIL: {os.path.basename(file_path)}")
                for issue in issues:
                    click.echo(f"  - {issue}")
            else:
                click.echo(f"OK: {os.path.basename(file_path)}")
    
    if has_error:
        exit(1)

@cli.command()
@click.option('--source', type=click.Choice(['hilda', 'cuigh', 'jermic', 'jimmy', 'mickorix', 'picotrex', 'zerolu', 'murattasdemir', 'supermaker', 'muset', 'youmind', 'all']), default='all', help='Source to extract from')
def extract(source):
    """Extract prompts from submodules."""
    click.echo(f"Extracting data from {source}...")
    
    total = 0
    
    if source in ['hilda', 'all']:
        click.echo("Running HildaExtractor...")
        extractor = HildaExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from HildaM.")
        total += count
        
    if source in ['cuigh', 'all']:
        click.echo("Running CuighExtractor...")
        extractor = CuighExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from Cuigh.")
        total += count

    if source in ['jermic', 'all']:
        click.echo("Running JermicExtractor...")
        extractor = JermicExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from Jermic.")
        total += count
        
    if source in ['jimmy', 'all']:
        click.echo("Running JimmyLvExtractor...")
        extractor = JimmyLvExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from JimmyLv.")
        total += count

    if source in ['mickorix', 'all']:
        click.echo("Running MickorixExtractor...")
        extractor = MickorixExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from Mickorix.")
        total += count
        
    if source in ['picotrex', 'all']:
        click.echo("Running PicoTrexExtractor...")
        extractor = PicoTrexExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from PicoTrex.")
        total += count
        
    if source in ['zerolu', 'all']:
        click.echo("Running ZeroLuExtractor...")
        extractor = ZeroLuExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from ZeroLu.")
        total += count
        
    if source in ['murattasdemir', 'all']:
        click.echo("Running MurattasdemirExtractor...")
        extractor = MurattasdemirExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from Murattasdemir.")
        total += count

    if source in ['supermaker', 'all']:
        click.echo("Running SuperMakerExtractor...")
        extractor = SuperMakerExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from SuperMaker.")
        total += count

    if source in ['muset', 'all']:
        click.echo("Running MusetExtractor...")
        extractor = MusetExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from MusetAI.")
        total += count

    if source in ['youmind', 'all']:
        click.echo("Running YouMindExtractor...")
        extractor = YouMindExtractor()
        count = extractor.extract()
        click.echo(f"Extracted {count} entries from YouMind.")
        total += count
        
    click.echo(f"Total extracted: {total}")

@cli.command()
def index():
    """Generate a JSON index of all database entries."""
    click.echo("Generating index...")
    files = glob.glob(os.path.join(DATABASE_DIR, "**", "*.md"), recursive=True)
    index_data = []
    
    for file_path in files:
        if os.path.basename(file_path).startswith('.'):
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            metadata, _ = parse_frontmatter(content)
            
            if metadata:
                entry = metadata.copy()
                # Add relative path from database dir
                rel_path = os.path.relpath(file_path, DATABASE_DIR)
                entry['path'] = rel_path
                entry['language'] = metadata.get('language', 'en')
                index_data.append(entry)
            else:
                # Fallback for failed parsing?
                pass

    index_path = os.path.join(DATABASE_DIR, "index.json")
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2)
        
    click.echo(f"Index generated with {len(index_data)} entries at {index_path}")

@cli.command()
@click.argument('query')
def search(query):
    """Search the database index."""
    index_path = os.path.join(DATABASE_DIR, "index.json")
    if not os.path.exists(index_path):
        click.echo("Index not found. Run 'python manage_db.py index' first.")
        return

    with open(index_path, 'r') as f:
        index_data = json.load(f)
        
    query = query.lower()
    results = []
    
    for entry in index_data:
        # Search in title, author, and tags
        match = False
        if query in entry.get('title', '').lower():
            match = True
        elif query in entry.get('author', '').lower():
            match = True
        elif any(query in tag.lower() for tag in entry.get('tags', [])):
            match = True
            
        if match:
            results.append(entry)
            
    if not results:
        click.echo("No results found.")
        return
        
    click.echo(f"Found {len(results)} results:")
    click.echo("-" * 86)
    click.echo(f"{'TITLE':<40} | {'AUTHOR':<20} | {'PATH':<20}")
    click.echo("-" * 86)
    
    for res in results:
        title = res.get('title', 'Unknown')
        author = res.get('author', 'Unknown')
        path = res.get('path', '')
        
        if len(title) > 38: title = title[:35] + "..."
        if len(author) > 18: author = author[:15] + "..."
        
        click.echo(f"{title:<40} | {author:<20} | {path:<20}")

@cli.command()
@click.option('--port', default=8000, help='Port to serve on.')
def serve(port):
    """Start the Web Viewer."""
    handler = http.server.SimpleHTTPRequestHandler
    
    # Custom class to allow address reuse
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    url = f"http://localhost:{port}/viewer.html"
    click.echo(f"Starting server at {url}")
    click.echo("Press Ctrl+C to stop.")
    
    # Auto open browser
    webbrowser.open(url)
    
    try:
        with ReusableTCPServer(("", port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                click.echo("\nServer stopped.")
    except OSError as e:
        if e.errno == 48:
            click.echo(f"\nError: Port {port} is already in use.")
            click.echo(f"Try using a different port: python manage_db.py serve --port {port+1}")
        else:
            raise e

if __name__ == '__main__':
    cli()
