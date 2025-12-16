"""Search engine module using Meilisearch."""

from typing import List, Dict, Optional, Any
from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from .config import MEILISEARCH_URL, MEILISEARCH_API_KEY, INDEX_NAME, SEARCH_RESULT_LIMIT


class SearchEngine:
    """Meilisearch-based search engine."""
    
    def __init__(self):
        """Initialize Meilisearch client."""
        self.client = Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
        self.index_name = INDEX_NAME
        self.index = None
    
    def connect_to_meilisearch(self) -> bool:
        """Connect to Meilisearch and get index."""
        try:
            self.index = self.client.index(self.index_name)
            # Try to get index info to verify connection
            self.index.get_raw_info()
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
            # Create index if it doesn't exist
            try:
                self.index = self.client.create_index(self.index_name, {"primaryKey": "id"})
            except MeilisearchApiError as e:
                if e.status_code == 409:
                    # Index already exists, get it
                    self.index = self.client.index(self.index_name)
                else:
                    raise
            
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
            
            print(f"Index '{self.index_name}' created/configured successfully")
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
            
            for i in range(0, total, batch_size):
                batch = documents[i:i + batch_size]
                self.index.add_documents(batch)
                print(f"Indexed {min(i + batch_size, total)}/{total} documents")
            
            # Wait for indexing to complete
            self.index.wait_for_task(self.index.get_tasks()["results"][0]["uid"])
            
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
                "q": query,
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
            
            results = self.index.search(**search_params)
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


# Global search engine instance
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get or create global search engine instance."""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
