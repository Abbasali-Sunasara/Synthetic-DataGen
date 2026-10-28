"""Business services module."""

from database import db

def process_user_registration(username: str, email: str) -> dict:
    """Process user creation and save via database module."""
    query_string = f"INSERT INTO users (username, email) VALUES ('{username}', '{email}')"
    result = db.query(query_string)
    
    return {
        "user": username,
        "email": email,
        "db_response": result
    }

def fetch_user_data(user_id: str) -> dict:
    """Fetch user record from database."""
    query_string = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.query(query_string)