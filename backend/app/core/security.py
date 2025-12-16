import bcrypt
from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    digest = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(digest, hashed_password)

def get_password_hash(password: str) -> str:
    print(f"DEBUG_SEC: 收到密碼，長度: {len(password)}")
    digest = hashlib.sha256(password.encode()).hexdigest()
    print(f"DEBUG_SEC: 哈希後密碼，長度: {len(digest)}")
    return pwd_context.hash(digest)