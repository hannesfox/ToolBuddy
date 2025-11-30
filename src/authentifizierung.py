from typing import Optional
from .daten_manager import DataManager
from .modelle import User

class AuthManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_user: Optional[User] = None

    def login(self, username, password) -> bool:
        users = self.data_manager.load_users()
        
        print(f"[AUTH] Login attempt for: '{username}'")
        print(f"[AUTH] Loaded {len(users)} users from CSV")
        
        for user_data in users:
            print(f"[AUTH] Checking user: '{user_data['Username']}' (Role: {user_data['Role']})")
            if user_data['Username'] == username:
                print(f"[AUTH] Username matched!")
                # Check if user has no password (empty string)
                if user_data['Password'] == '':
                    print(f"[AUTH] Passwordless login accepted")
                    # Passwordless login - accept any password or empty
                    self.current_user = User(username=username, role=user_data['Role'])
                    return True
                else:
                    # Regular password check
                    hashed_pw = self.data_manager.hash_password(password)
                    print(f"[AUTH] Hashed password: {hashed_pw}")
                    print(f"[AUTH] Expected password: {user_data['Password']}")
                    if user_data['Password'] == hashed_pw:
                        print(f"[AUTH] Password matched!")
                        self.current_user = User(username=username, role=user_data['Role'])
                        return True
                    else:
                        print(f"[AUTH] Password mismatch!")
        print(f"[AUTH] Login failed - no matching user found")
        return False

    def login_as_guest(self):
        """Logs in as a default guest user."""
        self.current_user = User(username="User", role="user")

    def verify_admin_password(self, password) -> bool:
        """Checks if the provided password matches the admin password."""
        users = self.data_manager.load_users()
        hashed_pw = self.data_manager.hash_password(password)
        
        for user_data in users:
            if user_data['Role'] == 'admin' and user_data['Password'] == hashed_pw:
                return True
        return False

    def logout(self):
        self.current_user = None

    def is_admin(self) -> bool:
        return self.current_user and self.current_user.role == 'admin'

    def is_lager_admin(self) -> bool:
        """Returns True if user is admin OR lager admin"""
        return self.current_user and self.current_user.role in ['admin', 'lager']

