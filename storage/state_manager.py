# storage/state_manager.py
"""
State Manager for Pause/Resume
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

class StateManager:
    """Manage crawl state for pause/resume"""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
    
    def save(self, state: Dict[str, Any]):
        """Save current state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception:
            pass
    
    def load(self, state_file: Optional[Path] = None) -> Optional[Dict]:
        """Load state from file"""
        filepath = state_file or self.state_file
        
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return None
    
    def clear(self):
        """Clear state file"""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except Exception:
            pass
    
    def exists(self) -> bool:
        """Check if state file exists"""
        return self.state_file.exists()
