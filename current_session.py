from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
# Store hashed admin password

users = {
    "admin": generate_password_hash("123")
}
 

class CurrentSession:

    def authenticate(username, password):
        if username in users and check_password_hash(users[username], password):
            return True
        return False
    
    def isLoggedIn():
        return "username" not in session