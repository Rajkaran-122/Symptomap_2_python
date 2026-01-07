
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Configure structured logger
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.msg,
            "logger": record.name
        }
        
        # Merge extra fields if present
        if hasattr(record, "audit_data"):
            log_obj.update(record.audit_data)
            
        return json.dumps(log_obj)

# Setup logger
audit_logger = logging.getLogger("symptomap.audit")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
audit_logger.addHandler(handler)
audit_logger.setLevel(logging.INFO)

def log_audit_event(
    event: str,
    actor_id: str,
    actor_role: str,
    ip_address: str,
    status: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Log a secure audit event in JSON format.
    
    Args:
        event: Name of the action (e.g., "USER_LOGIN", "ALERT_CREATED")
        actor_id: ID of the user performing the action
        actor_role: Role of the user
        ip_address: Source IP
        status: "SUCCESS" or "FAILURE"
        metadata: Additional context (e.g., resource_id)
    """
    audit_data = {
        "actor": {
            "id": actor_id,
            "role": actor_role,
            "ip": ip_address
        },
        "action": {
            "status": status,
            "metadata": metadata or {}
        }
    }
    
    # Pass structured data as 'extra' for the formatter (or attach securely)
    # Using 'extra' dict in standard logging is tricky with custom formatters 
    # manipulating 'record'. simpler to just pass the dict.
    
    # We'll attach it to the record implicitly by creating a properly formatted log message
    # or better, use the extra dict capability of the logging module if we refine the Formatter.
    # For robust usage here, let's inject it into the `extra` param.
    
    audit_logger.info(event, extra={"audit_data": audit_data})
