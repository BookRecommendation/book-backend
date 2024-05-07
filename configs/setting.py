from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    _dbuser = "postgres"
    _dbpass = "postgres"
    _dbhost = "localhost"
    _dbport = "5432"
    _dbname = "books"
    _DATABASE_URL = f"postgresql://{_dbuser}:{_dbpass }@{_dbhost}:{_dbport}/{_dbname}"
    _host = "0.0.0.0"
    _port = 8000
    _isdebug = True
    _isreload = True
    SECRET_KEY: str = "book!@#$#@!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FILE_SESSION_TYPE = "memcached"
    FILE_SECRET_KEY = "bookfilemanage!@#$"
   
settings = Settings()