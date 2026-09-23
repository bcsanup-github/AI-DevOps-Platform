import hashlib
import hmac
import secrets

ITERATIONS = 390_000


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS)
        return f"pbkdf2_sha256${ITERATIONS}${salt}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        try:
            _, iterations, salt, expected = stored.split("$")
        except ValueError:
            return False

        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(digest.hex(), expected)
