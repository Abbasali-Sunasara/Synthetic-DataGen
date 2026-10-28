"""Main API entry point module."""

from services import process_user_registration, fetch_user_data

class APIRouter:
    """Mock router class."""
    def __init__(self):
        self.routes = []

    def get(self, path: str):
        def decorator(func):
            self.routes.append({"path": path, "method": "GET"})
            return func
        return decorator

    def post(self, path: str):
        def decorator(func):
            self.routes.append({"path": path, "method": "POST"})
            return func
        return decorator

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@router.post("/users")
def create_user(username: str, email: str):
    """Create user endpoint utilizing the services module."""
    return process_user_registration(username, email)

@router.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user endpoint."""
    return fetch_user_data(user_id)

if __name__ == "__main__":
    print("Starting application...")