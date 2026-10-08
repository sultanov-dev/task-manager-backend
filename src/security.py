from pwdlib import PasswordHash

password_hash_fn = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash_fn.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash_fn.verify(plain, hashed)
