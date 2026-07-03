import secrets
import string


def generate_secure_password(length: int = 24) -> str:
    """
        генерация криптографически стойкого пароля
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&-_=+"

    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                sum(c.isdigit() for c in password) >= 3 and
                any(c in "!@#$%^&-_=+" for c in password)):
            return password

if __name__ == "__main__":
    print(f"Password: {generate_secure_password(16)}")