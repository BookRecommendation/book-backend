import os
from fastapi.logger import logger
import jwt  # used for encoding and decoding jwt tokens
from fastapi import HTTPException, status, Depends  # used to handle error handling
from passlib.context import CryptContext  # used for hashing the password

# used to handle expiry time for tokens
from datetime import datetime, timedelta
from configs.setting import Settings

from handlers.database import get_db
from models.model import Student as User
from sqlalchemy.orm import Session


class AuthToken:
    settings = Settings()
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.SECRET_KEY

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return password== encoded_password

    def encode_token(self, username, role, id):
        user = {
            "username": username,
            "role": role,
            "id": id,
        }
        payload = {
            "exp": datetime.utcnow()
            + timedelta(days=0, minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "sub": user,
        }
        return jwt.encode(
            payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=self.settings.ALGORITHM
            )
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(
                status_code=401, detail="Scope for the token is invalid"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, username, role, id):
        user = {
            "username": username,
            "role": role,
            "id": id,
        }
        payload = {
            "exp": datetime.utcnow() + timedelta(days=0, hours=10),
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "sub": user,
        }
        return jwt.encode(
            payload, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
            if payload["scope"] == "refresh_token":
                userinfo = payload["sub"]
                new_token = self.encode_token(userinfo["username"],userinfo["role"],userinfo["id"])
                refresh_token = self.encode_refresh_token(userinfo["username"],userinfo["role"],userinfo["id"])
                return new_token,refresh_token
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
