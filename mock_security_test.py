"""
Mock module to test AI Codebase Mapper Security & Container Heuristics.

Contains intentionally flagged anti-patterns:
1. Hardcoded API key/secret string
2. Production debug flag enabled
3. Sensitive write route without authentication
"""

import os
from fastapi import FastAPI

app = FastAPI()

# 1. Hardcoded Secret / API Key Anti-Pattern
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE_SECRET_KEY_12345"
DB_PASSWORD = "super_secret_admin_password_2026"

# 2. Debug Mode Enabled Anti-Pattern
DEBUG = True
IS_PRODUCTION = False

@app.get("/health")
def health_check():
    """Unauthenticated health check (Normal endpoint)."""
    return {"status": "ok"}

# 3. Sensitive / Write Route missing Auth Dependency
@app.post("/api/v1/users/delete")
def delete_user_account(user_id: int):
    """
    Sensitive write operation with no detected auth decorator or dependency.
    Should trigger 'route_without_detected_auth_dependency' warning.
    """
    return {"status": "deleted", "user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    # 4. Insecure Reload / Debug in execution block
    uvicorn.run("mock_security_test:app", host="0.0.0.0", port=8000, reload=True)
