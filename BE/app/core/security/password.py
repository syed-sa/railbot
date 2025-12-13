from passlib.context import CryptContext
class passwordManager:

    pwd_context = CryptContext(
        schemes=["argon2"],
        deprecated="auto"
    )
    
    @staticmethod
    def hash_password( password: str) -> str:
        return passwordManager.pwd_context.hash(password)
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return passwordManager.pwd_context.verify(password, hashed)