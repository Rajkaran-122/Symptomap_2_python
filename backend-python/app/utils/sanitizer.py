import bleach
from typing import Optional

def sanitize_html(text: Optional[str]) -> Optional[str]:
    """
    Sanitize HTML input to prevent XSS attacks.
    Removes all tags/attributes not explicitly allowed.
    """
    if text is None:
        return None
    
    # Allow only basic formatting tags securely
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a']
    allowed_attrs = {'a': ['href', 'title']}
    
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)
