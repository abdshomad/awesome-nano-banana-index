"""FastAPI web application for the search engine."""

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from typing import Optional, List, Dict, Any
from pathlib import Path
from .search import get_search_engine
from .indexer import build_index
from .config import BASE_DIR
import threading

app = FastAPI(
    title="Nano Banana Search Engine",
    description="Search engine for awesome-nano-banana-index",
    version="0.1.0"
)

# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main search page."""
    templates_dir = BASE_DIR / "templates"
    template_file = templates_dir / "index.html"
    
    if template_file.exists():
        # Load template file
        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()
        return HTMLResponse(content=template_content)
    else:
        # Simple HTML response if template not available
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nano Banana Search</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .search-box { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 20px; }
                .filters { margin-bottom: 20px; }
                .filters select, .filters input { margin-right: 10px; padding: 5px; }
                .results { margin-top: 20px; }
                .result-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
                .result-title { font-size: 18px; font-weight: bold; color: #2563eb; margin-bottom: 10px; }
                .result-meta { color: #666; font-size: 14px; margin-bottom: 5px; }
                .result-prompt { color: #333; margin-top: 10px; }
            </style>
        </head>
        <body>
            <h1>Nano Banana Search Engine</h1>
            <input type="text" id="searchQuery" class="search-box" placeholder="Search prompts, cases, and documentation...">
            <div class="filters">
                <select id="langFilter">
                    <option value="both">All Languages</option>
                    <option value="en">English</option>
                    <option value="zh">Chinese</option>
                </select>
                <select id="submoduleFilter">
                    <option value="">All Submodules</option>
                </select>
            </div>
            <div id="results" class="results"></div>
            <script>
                const searchQuery = document.getElementById('searchQuery');
                const langFilter = document.getElementById('langFilter');
                const submoduleFilter = document.getElementById('submoduleFilter');
                const resultsDiv = document.getElementById('results');
                
                let searchTimeout;
                
                async function performSearch() {
                    const query = searchQuery.value.trim();
                    if (!query) {
                        resultsDiv.innerHTML = '';
                        return;
                    }
                    
                    const params = new URLSearchParams({
                        q: query,
                        lang: langFilter.value,
                        submodule: submoduleFilter.value || ''
                    });
                    
                    try {
                        const response = await fetch(`/api/search?${params}`);
                        const data = await response.json();
                        displayResults(data);
                    } catch (error) {
                        resultsDiv.innerHTML = '<p>Error performing search</p>';
                    }
                }
                
                function displayResults(data) {
                    if (!data.hits || data.hits.length === 0) {
                        resultsDiv.innerHTML = '<p>No results found</p>';
                        return;
                    }
                    
                    let html = `<p>Found ${data.total} result(s)</p>`;
                    data.hits.forEach(hit => {
                        const title = hit.title_en || hit.title || 'Untitled';
                        html += `
                            <div class="result-item">
                                <div class="result-title">${title}</div>
                                ${hit.author ? `<div class="result-meta">Author: ${hit.author}</div>` : ''}
                                ${hit.submodule ? `<div class="result-meta">Submodule: ${hit.submodule}</div>` : ''}
                                ${hit.prompt_en || hit.prompt ? `<div class="result-prompt">${(hit.prompt_en || hit.prompt).substring(0, 200)}...</div>` : ''}
                                <div class="result-meta">Path: ${hit.path}</div>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                }
                
                searchQuery.addEventListener('input', () => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(performSearch, 300);
                });
                
                langFilter.addEventListener('change', performSearch);
                submoduleFilter.addEventListener('change', performSearch);
                
                // Load submodules
                fetch('/api/submodules')
                    .then(r => r.json())
                    .then(data => {
                        data.submodules.forEach(sub => {
                            const option = document.createElement('option');
                            option.value = sub;
                            option.textContent = sub;
                            submoduleFilter.appendChild(option);
                        });
                    });
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)


@app.get("/api/search")
async def search_api(
    q: str = Query(..., description="Search query"),
    lang: Optional[str] = Query("both", description="Language filter: zh, en, or both"),
    submodule: Optional[str] = Query(None, description="Filter by submodule (comma-separated for multiple)"),
    limit: Optional[int] = Query(20, description="Number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Search API endpoint."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    # Build filters
    filters = []
    if submodule:
        # Handle multiple submodules (comma-separated)
        submodules = [s.strip() for s in submodule.split(",") if s.strip()]
        if submodules:
            if len(submodules) == 1:
                filters.append(f"submodule = '{submodules[0]}'")
            else:
                # Multiple submodules: use OR condition
                submodule_filter = " OR ".join([f"submodule = '{s}'" for s in submodules])
                filters.append(f"({submodule_filter})")
    
    filter_str = " AND ".join(filters) if filters else None
    
    # Perform search
    results = search_engine.search(
        query=q,
        language=lang,
        filters=filter_str,
        limit=limit,
        offset=offset
    )
    
    return results


@app.get("/api/suggestions")
async def get_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: Optional[int] = Query(5, description="Number of suggestions")
):
    """Get search suggestions for autocomplete."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    suggestions = search_engine.get_suggestions(q, limit=limit)
    
    return {"suggestions": suggestions}


@app.get("/api/case/{case_id}")
async def get_case(case_id: str):
    """Get full case details by ID."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    case = search_engine.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case


@app.get("/api/submodules")
async def get_submodules():
    """List all submodules."""
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    submodules = search_engine.get_submodules()
    
    return {"submodules": submodules}


# Global flag to track if indexing is in progress
_indexing_in_progress = False

def run_indexing():
    """Run indexing in background thread."""
    global _indexing_in_progress
    _indexing_in_progress = True
    try:
        search_engine = get_search_engine()
        
        if not search_engine.connect_to_meilisearch():
            print("Error: Could not connect to Meilisearch")
            return
        
        # Check if index already exists and has documents
        if search_engine.is_indexed():
            print("Index already exists with documents. Skipping index creation and document indexing.")
            return
        
        # Create index if needed
        if not search_engine.create_index():
            print("Error: Could not create index")
            return
        
        # Build index
        documents = build_index(rebuild=False)
        
        if not documents:
            print("No documents found to index")
            return
        
        # Index documents
        if search_engine.index_documents(documents):
            print(f"Successfully indexed {len(documents)} documents")
        else:
            print("Error: Failed to index documents")
    except Exception as e:
        print(f"Error during indexing: {e}")
    finally:
        _indexing_in_progress = False

@app.post("/api/trigger-index")
async def trigger_index(background_tasks: BackgroundTasks):
    """Trigger index creation."""
    global _indexing_in_progress
    
    if _indexing_in_progress:
        return {"message": "Indexing already in progress", "status": "running"}
    
    search_engine = get_search_engine()
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    # Check if already indexed
    if search_engine.is_indexed():
        return {"message": "Index already exists", "status": "complete"}
    
    # Start indexing in background thread
    thread = threading.Thread(target=run_indexing, daemon=True)
    thread.start()
    
    return {"message": "Indexing started", "status": "started"}

@app.get("/api/index-status")
async def get_index_status():
    """Check if the index exists and has documents, with progress information."""
    global _indexing_in_progress
    
    search_engine = get_search_engine()
    
    if not search_engine.connect_to_meilisearch():
        raise HTTPException(status_code=503, detail="Search service unavailable")
    
    progress_info = search_engine.get_indexing_progress()
    
    # If indexing is in progress but we can't detect it from Meilisearch tasks,
    # use our global flag
    if _indexing_in_progress and not progress_info["indexed"]:
        progress_info["is_indexing"] = True
        if progress_info["progress"] == 0:
            progress_info["progress"] = 5  # Show some progress
    
    return {
        "indexed": progress_info["indexed"],
        "progress": progress_info["progress"],
        "document_count": progress_info["document_count"],
        "is_indexing": progress_info["is_indexing"] or _indexing_in_progress,
        "estimated_time_remaining": progress_info["estimated_time_remaining"],
        "message": "Index is ready" if progress_info["indexed"] else "Index is being created, please wait..."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
