
import sys
import os
import json
import logging
from io import StringIO

# Mock logging setup
stream = StringIO()
handler = logging.StreamHandler(stream)

# Import audit logger
sys.path.append(os.getcwd())
from app.core.audit import audit_logger, JsonFormatter, log_audit_event

# Configure test logger
handler.setFormatter(JsonFormatter())
audit_logger.handlers = [] # Clear existing
audit_logger.addHandler(handler)
audit_logger.setLevel(logging.INFO)

print("Running Audit Log Verification...")

try:
    # Trigger Event
    log_audit_event(
        event="TEST_EVENT",
        actor_id="user_123",
        actor_role="admin",
        ip_address="127.0.0.1",
        status="SUCCESS",
        metadata={"resource": "test_resource"}
    )
    
    # Verify Output
    output = stream.getvalue()
    print(f"\nRaw Log Output:\n{output}")
    
    log_json = json.loads(output)
    
    # Assertions
    assert log_json['event'] == "TEST_EVENT"
    assert log_json['actor']['id'] == "user_123"
    assert log_json['actor']['role'] == "admin"
    assert log_json['action']['status'] == "SUCCESS"
    assert "timestamp" in log_json
    
    print("✅ Audit Log Structure Verified!")

except Exception as e:
    print(f"❌ Verification Failed: {e}")
    sys.exit(1)
