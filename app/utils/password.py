import re

from passlib import pwd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 密码策略：8~128 位，至少包含一个字母和一个数字，且不含空白字符。
_PASSWORD_POLICY_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)\S{8,128}\Z")


def is_password_strong(password: str) -> bool:
    """返回密码是否满足系统强度要求。"""
    return bool(_PASSWORD_POLICY_RE.match(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_password() -> str:
    return pwd.genword()
