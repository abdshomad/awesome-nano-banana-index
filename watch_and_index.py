#!/usr/bin/env python3
"""
File watcher for automatic database re-indexing.
Monitors submodule directories for changes and triggers re-indexing.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debounce settings
DEBOUNCE_SECONDS = 5  # Wait 5 seconds after last change before re-indexing
last_change_time = None
reindex_scheduled = False


class RepoChangeHandler(FileSystemEventHandler):
    """Handler for file system events in repository directories."""
    
    def __init__(self):
        super().__init__()
        self.ignored_patterns = {
            '.git', '__pycache__', '.pyc', '.pyo', '.pyd',
            '.so', '.dll', '.dylib', '.DS_Store', '.venv',
            'node_modules', '.idea', '.vscode'
        }
    
    def should_ignore(self, path):
        """Check if the path should be ignored."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.ignored_patterns)
    
    def on_any_event(self, event):
        """Handle any file system event."""
        global last_change_time, reindex_scheduled
        
        # Ignore directory events and certain file patterns
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        # Update last change time
        last_change_time = time.time()
        
        if not reindex_scheduled:
            reindex_scheduled = True
            logger.info(f"Change detected: {event.src_path}")
            logger.info(f"Re-indexing scheduled in {DEBOUNCE_SECONDS} seconds...")


def run_indexer():
    """Run the search indexer."""
    global reindex_scheduled
    
    try:
        logger.info("Starting re-indexing...")
        result = subprocess.run(
            ["uv", "run", "python", "-m", "search", "index"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Re-indexing completed successfully!")
        if result.stdout:
            logger.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Re-indexing failed: {e}")
        if e.stderr:
            logger.error(e.stderr)
    finally:
        reindex_scheduled = False


def get_submodule_dirs():
    """Get list of submodule directories to watch."""
    base_dir = Path.cwd()
    submodule_dirs = []
    
    # Find all directories starting with 'awesome-' or 'Awesome-'
    for item in base_dir.iterdir():
        if item.is_dir() and (
            item.name.startswith('awesome-') or 
            item.name.startswith('Awesome-')
        ):
            submodule_dirs.append(item)
            logger.info(f"Watching: {item.name}")
    
    return submodule_dirs


def main():
    """Main function to start the file watcher."""
    global last_change_time
    
    logger.info("Starting file watcher for auto re-indexing...")
    
    # Get directories to watch
    watch_dirs = get_submodule_dirs()
    
    if not watch_dirs:
        logger.warning("No submodule directories found to watch!")
        return
    
    # Create observer and event handler
    event_handler = RepoChangeHandler()
    observer = Observer()
    
    # Schedule observers for each directory
    for watch_dir in watch_dirs:
        observer.schedule(event_handler, str(watch_dir), recursive=True)
    
    # Start observer
    observer.start()
    logger.info(f"Watching {len(watch_dirs)} directories for changes...")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            
            # Check if we should trigger re-indexing
            if reindex_scheduled and last_change_time:
                time_since_change = time.time() - last_change_time
                if time_since_change >= DEBOUNCE_SECONDS:
                    run_indexer()
                    last_change_time = None
    
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer.stop()
    
    observer.join()
    logger.info("File watcher stopped.")


if __name__ == "__main__":
    main()
