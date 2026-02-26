import subprocess
import json
import sys
import os
from typing import Dict

def scan_website(url: str, project_id: str) -> Dict:
    """Run scanner in separate process to avoid asyncio conflicts"""
    
    script_path = os.path.join(os.path.dirname(__file__), "..", "scanner_process.py")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, url, project_id],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        if result.returncode != 0:
            try:
                error_data = json.loads(result.stdout)
                raise RuntimeError(error_data.get("error", "Scanner failed"))
            except json.JSONDecodeError:
                raise RuntimeError(f"Scanner failed: {result.stderr or result.stdout}")
        
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Scan timeout - website took too long")
    except json.JSONDecodeError:
        raise RuntimeError("Scanner returned invalid data")
