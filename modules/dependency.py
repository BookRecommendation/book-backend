from fastapi import Request, Security, HTTPException,Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from modules.token import AuthToken
from handlers.database import get_db
from sqlalchemy.orm import Session
from fastapi.logger import logger
from models.model import  Student as User
security = HTTPBearer()
auth_handler = AuthToken()


async def AdminAuthHandler(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(security)
):
    data = auth_handler.decode_token(credentials.credentials)
    if data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")



async def AuthHandler(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(security),db: Session = Depends(get_db)
):
    data = auth_handler.decode_token(credentials.credentials)
    user = db.query(User).get(data["id"])
    logger.info(user.active)
    if not user.active:
        raise HTTPException(status_code=401, detail="User banned")
    if data["role"] != "admin" and data["role"] != "agent" and data["role"] != "sub":
        raise HTTPException(status_code=403, detail="Operation not permitted")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    user = auth_handler.decode_token(credentials.credentials)
    return user


async def RefreshToken(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(security)
):
    return  {"access_token":auth_handler.refresh_token(credentials.credentials)}
