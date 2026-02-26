import re
import logging
from urllib.parse import urlparse
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF attacks and ensure proper format.
    Only allows http and https protocols.
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check length
    if len(url) > 2048:
        return False
    
    try:
        parsed = urlparse(url)
        
        # Must have http or https scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Must have a valid hostname
        if not parsed.netloc:
            return False
        
        # Block localhost and private IPs to prevent SSRF
        hostname = parsed.netloc.split(':')[0].lower()
        
        # Block localhost variations
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            return False
        
        # Block private IP ranges (basic check)
        if hostname.startswith('10.') or hostname.startswith('192.168.') or hostname.startswith('172.'):
            return False
        
        return True
        
    except Exception:
        return False

def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to avoid leaking sensitive information.
    """
    error_str = str(error)
    
    # Remove file paths
    error_str = re.sub(r'[A-Za-z]:\\[^\s]+', '[PATH]', error_str)
    error_str = re.sub(r'/[^\s]+', '[PATH]', error_str)
    
    # Keep it generic
    if len(error_str) > 200:
        return "An error occurred during processing"
    
    return error_str
