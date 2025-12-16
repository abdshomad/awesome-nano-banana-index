"""CLI interface for the search engine."""

import click
from .indexer import build_index
from .search import get_search_engine


@click.group()
def cli():
    """Search engine CLI for awesome-nano-banana-index."""
    pass


@cli.command()
@click.option("--rebuild", is_flag=True, help="Rebuild the entire index")
def index(rebuild):
    """Build or rebuild the search index."""
    click.echo("Building search index...")
    
    search_engine = get_search_engine()
    
    # Connect to Meilisearch
    if not search_engine.connect_to_meilisearch():
        click.echo(click.style("Error: Could not connect to Meilisearch", fg="red"))
        click.echo("Make sure Meilisearch is running (docker-compose up -d)")
        return
    
    # Create index if needed
    if not search_engine.create_index():
        click.echo(click.style("Error: Could not create index", fg="red"))
        return
    
    # Build index
    documents = build_index(rebuild=rebuild)
    
    if not documents:
        click.echo(click.style("No documents found to index", fg="yellow"))
        return
    
    # Index documents
    if search_engine.index_documents(documents):
        click.echo(click.style(f"Successfully indexed {len(documents)} documents", fg="green"))
    else:
        click.echo(click.style("Error: Failed to index documents", fg="red"))


@cli.command()
@click.argument("query")
@click.option("--lang", type=click.Choice(["zh", "en", "both"]), default="both", help="Language filter")
@click.option("--field", type=click.Choice(["title", "prompt", "all"]), default="all", help="Field to search")
@click.option("--submodule", help="Filter by submodule name")
@click.option("--limit", type=int, default=20, help="Number of results to return")
@click.option("--offset", type=int, default=0, help="Offset for pagination")
def search(query, lang, field, submodule, limit, offset):
    """Search the index."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        click.echo(click.style("Error: Could not connect to Meilisearch", fg="red"))
        return
    
    # Build filters
    filters = []
    if submodule:
        filters.append(f"submodule = '{submodule}'")
    
    if field != "all":
        # Note: Meilisearch doesn't support field-specific search directly in filters
        # This would require custom searchable attributes configuration
        pass
    
    filter_str = " AND ".join(filters) if filters else None
    
    # Perform search
    results = search_engine.search(
        query=query,
        language=lang,
        filters=filter_str,
        limit=limit,
        offset=offset
    )
    
    hits = results.get("hits", [])
    total = results.get("total", 0)
    
    if not hits:
        click.echo(click.style("No results found", fg="yellow"))
        return
    
    # Display results
    click.echo(f"\nFound {total} result(s)\n")
    
    for i, hit in enumerate(hits, 1):
        click.echo(click.style(f"{i}. ", fg="cyan") + click.style(
            hit.get("title_en") or hit.get("title") or "Untitled",
            fg="green",
            bold=True
        ))
        
        if hit.get("author"):
            click.echo(f"   Author: {hit.get('author')}")
        
        if hit.get("submodule"):
            click.echo(f"   Submodule: {click.style(hit.get('submodule'), fg='blue')}")
        
        if hit.get("prompt_en") or hit.get("prompt"):
            prompt = hit.get("prompt_en") or hit.get("prompt", "")
            if len(prompt) > 100:
                prompt = prompt[:100] + "..."
            click.echo(f"   Prompt: {prompt}")
        
        click.echo(f"   Path: {hit.get('path', '')}")
        click.echo()


@cli.command()
def list_submodules():
    """List all indexed submodules."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        click.echo(click.style("Error: Could not connect to Meilisearch", fg="red"))
        return
    
    submodules = search_engine.get_submodules()
    
    if not submodules:
        click.echo(click.style("No submodules found", fg="yellow"))
        return
    
    click.echo(f"\nFound {len(submodules)} submodule(s):\n")
    for submodule in submodules:
        click.echo(f"  - {click.style(submodule, fg='blue')}")


@cli.command()
@click.argument("case_id")
def show(case_id):
    """Show details of a specific case by ID."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        click.echo(click.style("Error: Could not connect to Meilisearch", fg="red"))
        return
    
    case = search_engine.get_case_by_id(case_id)
    
    if not case:
        click.echo(click.style(f"Case with ID '{case_id}' not found", fg="yellow"))
        return
    
    # Display case details
    click.echo("\n" + click.style("Case Details", fg="green", bold=True) + "\n")
    
    if case.get("title_en"):
        click.echo(f"Title (EN): {case.get('title_en')}")
    if case.get("title"):
        click.echo(f"Title (ZH): {case.get('title')}")
    
    if case.get("author"):
        click.echo(f"Author: {case.get('author')}")
        if case.get("author_link"):
            click.echo(f"Author Link: {case.get('author_link')}")
    
    if case.get("prompt_en"):
        click.echo(f"\nPrompt (EN):\n{case.get('prompt_en')}")
    if case.get("prompt"):
        click.echo(f"\nPrompt (ZH):\n{case.get('prompt')}")
    
    if case.get("submodule"):
        click.echo(f"\nSubmodule: {case.get('submodule')}")
    
    if case.get("path"):
        click.echo(f"Path: {case.get('path')}")
    
    if case.get("image"):
        click.echo(f"Image: {case.get('image')}")


if __name__ == "__main__":
    cli()
