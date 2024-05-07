from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from modules.token import AuthToken
from models.schema import UserSchema, LoginSchema
from fastapi.logger import logger
from models.model import  Admin as User
from models.model import  Student
from .database import get_db,SessionLocal
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging
router = APIRouter()

auth_handler = AuthToken()


@router.post("/stulogin", tags=["auth"])
def login(user_details: LoginSchema, db: Session = Depends(get_db)):
    logger.info(user_details)
    user = db.query(Student).filter(Student.username == user_details.username).first()
    if user is None:
        return HTTPException(status_code=400, detail="Invalid username")
    if not user.active:
        return HTTPException(status_code=400, detail="Invalid user")
    if not auth_handler.verify_password(user_details.password, user.password):
        return HTTPException(status_code=400, detail="Invalid password")
    access_token = auth_handler.encode_token(user.username, "student", user.id)
    refresh_token = auth_handler.encode_refresh_token(
        user.username, "student", user.id
    )
    content = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "username": user.username,
    }
    logger.info(content)
    response = JSONResponse(content=jsonable_encoder(content))
    return response




from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        db = SessionLocal()
        form = await request.form()
        username, password = form["username"], form["password"]
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.active or auth_handler.verify_password(password, user.password):
            return False
        content = {"username": user.username,"role": user.role,"id":user.id}
        request.session.update({"token": content})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True