from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.logger import logger
import logging
from fastapi.middleware.cors import CORSMiddleware
import os.path as op
from modules.token import AuthToken
import datetime
from sqladmin import Admin, ModelView



def create_app():
    from handlers.login import AdminAuth
    from handlers.database import SessionLocal, engine
    from starlette.middleware.sessions import SessionMiddleware

    authentication_backend = AdminAuth(secret_key="bookRecom@#$%")
    app = FastAPI()
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    auth_handler = AuthToken()
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from modules.dependency import AdminAuthHandler, AuthHandler,RefreshToken
    from handlers import login, upload,book
    import handlers.database as app_model
    from models.mview import AdminView,StudentView,BookView,RatingView,BannerView,LibraryView,BorrowView
    from models.model import Admin as User
    admin.add_view(AdminView)
    admin.add_view(StudentView)
    admin.add_view(BookView)
    admin.add_view(RatingView)
    admin.add_view(BannerView)
    admin.add_view(LibraryView)
    admin.add_view(BorrowView)
    app_model.Base.metadata.create_all(bind=engine)
    logging.basicConfig(
       format='Book:{levelname:7} {message}', style='{', level=logging.DEBUG)
    
    app.include_router(upload.upload_router,dependencies=[Depends(AuthHandler)])
    app.include_router(login.router)
    app.include_router(book.router)
    app.include_router(upload.read_router)
    @app.on_event("startup")
    async def startup_event():
        user_data = [
            {
                "username": "admin",
                "password": "admin@dmin",
                "role": "admin",
                "email": "admin@gmail.com",
            },
        ]
        db = SessionLocal()
        for user in user_data:
            is_user = db.query(User).filter(User.username == user["username"]).first()
            if not is_user:
                logger.info("User  Does not Exist")
                hashed_password = auth_handler.encode_password(user["password"])
                db_user = User(
                    username=user["username"],
                    password=hashed_password,
                    role="admin",
                )
                db.add(db_user)
                db.commit()
            else:
                logger.info(
                    user["username"]
                    + " Already Exists with role "
                    + user["role"]
                )
        logger.info("Database Startup Complete")

    return app


app = create_app()
