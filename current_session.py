from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from model import db, Users

# Store hashed admin password
admin_credentials = {
    "admin": generate_password_hash("123")
}

class CurrentSession:
    @staticmethod
    def authenticate(username, password):
        global userRole

        print(f"Trying to log in user: {username}")
        
        # Check admin credentials
        if username in admin_credentials and check_password_hash(admin_credentials[username], password):
            print("Logged in as admin")
            userRole = "admin"
            return True
        
        # Check database user
        print("Checking database for user")
        user = Users.query.filter_by(username=username).first()
        if user:
            if (user.password == password):
                userRole = user.role
                print(f"User role is: {userRole}")
                return True    
                  
        return False
    
    @staticmethod
    def isLoggedIn():
        status = "username" in session
        return status
    
    @staticmethod
    def notLoggedIn():
        return not CurrentSession.isLoggedIn()
    
    @staticmethod
    def getRole():
        return userRole
    
    @staticmethod
    def getUsername():
        username = session.get("username", None)  # Get username from session
        return username