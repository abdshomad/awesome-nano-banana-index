"""Search engine module using Meilisearch."""

from typing import List, Dict, Optional, Any
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from .config import MEILISEARCH_URL, MEILISEARCH_API_KEY, INDEX_NAME, SEARCH_RESULT_LIMIT


class SearchEngine:
    """Meilisearch-based search engine."""
    
    def __init__(self):
        """Initialize Meilisearch client."""
        # Pass None if API key is empty to allow unauthenticated access
        api_key = MEILISEARCH_API_KEY if MEILISEARCH_API_KEY else None
        self.client = Client(MEILISEARCH_URL, api_key)
        self.index_name = INDEX_NAME
        self.index = None
    
    def connect_to_meilisearch(self) -> bool:
        """Connect to Meilisearch and get index."""
        try:
            self.index = self.client.index(self.index_name)
            # Try to get index stats to verify connection
            # If index doesn't exist, this will raise an error which we'll catch
            try:
                self.index.get_stats()
            except MeilisearchApiError as e:
                if e.status_code == 404:
                    # Index doesn't exist yet, that's okay
                    pass
                else:
                    raise
            return True
        except MeilisearchApiError as e:
            if e.status_code == 404:
                # Index doesn't exist yet, that's okay
                return True
            print(f"Error connecting to Meilisearch: {e}")
            return False
        except Exception as e:
            print(f"Error connecting to Meilisearch: {e}")
            return False
    
    def create_index(self) -> bool:
        """Create Meilisearch index with proper settings."""
        try:
            index_created = False
            # Create index if it doesn't exist
            try:
                task = self.client.create_index(self.index_name, {"primaryKey": "id"})
                # Wait for the task to complete
                self.client.wait_for_task(task.task_uid)
                # Get the index object
                self.index = self.client.index(self.index_name)
                index_created = True
            except MeilisearchApiError as e:
                if e.status_code == 409:
                    # Index already exists, get it
                    self.index = self.client.index(self.index_name)
                    # Check if index already has documents
                    try:
                        stats = self.index.get_stats()
                        document_count = stats.get("numberOfDocuments", 0)
                        if document_count > 0:
                            # Index already exists with documents, skip reconfiguration
                            print(f"Index '{self.index_name}' already exists with {document_count} documents. Skipping reconfiguration.")
                            return True
                    except Exception:
                        # If we can't get stats, continue with configuration
                        pass
                else:
                    raise
            
            # Only configure attributes if index was just created or is empty
            # Configure searchable attributes
            self.index.update_searchable_attributes([
                "title",
                "title_en",
                "prompt",
                "prompt_en",
                "author",
                "content"
            ])
            
            # Configure filterable attributes
            self.index.update_filterable_attributes([
                "submodule",
                "type",
                "capability_code",
                "language",
                "author"
            ])
            
            # Configure sortable attributes
            self.index.update_sortable_attributes([
                "submodule",
                "type"
            ])
            
            if index_created:
                print(f"Index '{self.index_name}' created and configured successfully")
            else:
                print(f"Index '{self.index_name}' configured successfully")
            return True
            
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def index_documents(self, documents: List[Dict]) -> bool:
        """Bulk index documents to Meilisearch."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return False
        
        try:
            # Index documents in batches
            batch_size = 100
            total = len(documents)
            task_uids = []
            
            for i in range(0, total, batch_size):
                batch = documents[i:i + batch_size]
                task = self.index.add_documents(batch)
                task_uids.append(task.task_uid)
                print(f"Indexed {min(i + batch_size, total)}/{total} documents")
            
            # Wait for all indexing tasks to complete (with longer timeout)
            for task_uid in task_uids:
                try:
                    self.index.wait_for_task(task_uid, timeout_in_ms=60000)  # 60 second timeout
                except Exception as e:
                    print(f"Warning: Task {task_uid} may still be processing: {e}")
                    # Continue anyway - the task might complete later
            
            print(f"Successfully indexed {total} documents")
            return True
            
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return False
    
    def search(
        self,
        query: str,
        language: Optional[str] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Perform search using Meilisearch."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return {"hits": [], "total": 0, "offset": 0, "limit": 0}
        
        try:
            search_params = {
                "limit": limit or SEARCH_RESULT_LIMIT,
                "offset": offset,
            }
            
            # Build filter string
            filter_parts = []
            if language and language != "both":
                if language == "zh":
                    # Search in Chinese fields
                    filter_parts.append("language = 'zh' OR language = 'both'")
                elif language == "en":
                    # Search in English fields
                    filter_parts.append("language = 'en' OR language = 'both'")
            
            if filters:
                filter_parts.append(filters)
            
            if filter_parts:
                search_params["filter"] = " AND ".join(filter_parts)
            
            # Meilisearch search() takes query as first positional arg, params as second
            results = self.index.search(query, search_params)
            return results
            
        except Exception as e:
            print(f"Error performing search: {e}")
            return {"hits": [], "total": 0, "offset": 0, "limit": 0}
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """Retrieve specific case by ID."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return None
        
        try:
            # Use get_document to fetch by primary key
            document = self.index.get_document(case_id)
            return document
        except MeilisearchApiError as e:
            if e.status_code == 404:
                return None
            print(f"Error getting case by ID: {e}")
            return None
        except Exception as e:
            print(f"Error getting case by ID: {e}")
            return None
    
    def get_submodules(self) -> List[str]:
        """Get list of all unique submodules."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return []
        
        # Check if index is indexed first
        if not self.is_indexed():
            return []
        
        try:
            # Search with empty query to get all documents, then extract unique submodules
            # Use a large limit to get all documents
            results = self.index.search("", {"limit": 10000})
            submodules = set()
            
            for doc in results.get("hits", []):
                if "submodule" in doc:
                    submodules.add(doc["submodule"])
            
            return sorted(list(submodules))
            
        except Exception as e:
            print(f"Error getting submodules: {e}")
            return []
    
    def is_indexed(self) -> bool:
        """Check if the index exists and has documents."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return False
        
        try:
            # Try to get index stats to check if it exists and has documents
            try:
                stats = self.index.get_stats()
                document_count = stats.number_of_documents if hasattr(stats, 'number_of_documents') else 0
                return document_count > 0
            except MeilisearchApiError as e:
                if e.status_code == 404:
                    # Index doesn't exist
                    return False
                raise
        except Exception as e:
            print(f"Error checking index status: {e}")
            return False
    
    def get_indexing_progress(self) -> Dict[str, Any]:
        """Get indexing progress information."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return {
                    "indexed": False,
                    "progress": 0,
                    "document_count": 0,
                    "is_indexing": False,
                    "estimated_time_remaining": None
                }
        
        try:
            # Get index stats
            try:
                stats = self.index.get_stats()
                document_count = stats.number_of_documents if hasattr(stats, 'number_of_documents') else 0
                is_indexed = document_count > 0
                
                # Check for active indexing tasks
                is_indexing = False
                progress = 100 if is_indexed else 0
                
                try:
                    # Get recent tasks to check if indexing is in progress
                    tasks = self.index.get_tasks({"limit": 10})
                    for task in tasks.get("results", []):
                        task_type = task.get("type", "")
                        task_status = task.get("status", "")
                        # Check for document addition tasks
                        if task_type in ["documentAdditionOrUpdate", "documentAddition"]:
                            if task_status in ["enqueued", "processing"]:
                                is_indexing = True
                                # Try to get progress from task details
                                if "details" in task:
                                    details = task.get("details", {})
                                    indexed_documents = details.get("indexedDocuments", 0)
                                    total_documents = details.get("receivedDocuments", 0)
                                    if total_documents > 0:
                                        progress = min(95, int((indexed_documents / total_documents) * 100))
                                break
                except Exception:
                    # If we can't get tasks, assume not indexing
                    pass
                
                # Estimate time remaining (rough estimate: 1-3 minutes for typical indexing)
                estimated_time_remaining = None
                if is_indexing and progress < 100:
                    # Rough estimate: if progress is 0, assume 2-3 minutes
                    # If progress is > 0, estimate based on remaining percentage
                    if progress == 0:
                        estimated_time_remaining = 180  # 3 minutes
                    else:
                        # Estimate: remaining percentage * 2 seconds per percent
                        remaining_percent = 100 - progress
                        estimated_time_remaining = max(30, int(remaining_percent * 2))
                
                return {
                    "indexed": is_indexed,
                    "progress": progress,
                    "document_count": document_count,
                    "is_indexing": is_indexing,
                    "estimated_time_remaining": estimated_time_remaining
                }
            except MeilisearchApiError as e:
                if e.status_code == 404:
                    # Index doesn't exist
                    return {
                        "indexed": False,
                        "progress": 0,
                        "document_count": 0,
                        "is_indexing": False,
                        "estimated_time_remaining": 180  # 3 minutes estimate
                    }
                raise
        except Exception as e:
            print(f"Error getting indexing progress: {e}")
            return {
                "indexed": False,
                "progress": 0,
                "document_count": 0,
                "is_indexing": False,
                "estimated_time_remaining": None
            }
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get search suggestions for autocomplete."""
        if not self.index:
            if not self.connect_to_meilisearch():
                return []
        
        if not query or len(query.strip()) < 2:
            return []
        
        try:
            # Perform a search with a small limit to get suggestions
            search_params = {
                "q": query.strip(),
                "limit": limit,
                "attributesToRetrieve": ["title", "title_en", "prompt", "prompt_en"],
            }
            
            results = self.index.search(**search_params)
            suggestions = []
            
            for hit in results.get("hits", []):
                # Extract the most relevant text for the suggestion
                suggestion_text = hit.get("title_en") or hit.get("title") or ""
                if not suggestion_text:
                    suggestion_text = (hit.get("prompt_en") or hit.get("prompt") or "")[:50]
                
                if suggestion_text:
                    suggestions.append({
                        "text": suggestion_text,
                        "title": hit.get("title_en") or hit.get("title") or "",
                        "title_en": hit.get("title_en", ""),
                        "title_zh": hit.get("title", ""),
                    })
            
            return suggestions
            
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return []


# Global search engine instance
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get or create global search engine instance."""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
