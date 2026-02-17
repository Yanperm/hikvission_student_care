from werkzeug.security import generate_password_hash, check_password_hash

class PasswordManager:
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    @staticmethod
    def verify_password(password, password_hash):
        return check_password_hash(password_hash, password)

password_manager = PasswordManager()
