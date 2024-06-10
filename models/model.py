from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Float,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
    ARRAY,
    Boolean,
    BigInteger
)
from handlers.database import Base
import datetime
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType

from fastapi_storages import FileSystemStorage 
storage = FileSystemStorage(path="uploads/")



class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    #postImage = Column(ARRAY(JSON), nullable=True)
    active = Column(Boolean, unique=False, default=True)
    postImage = Column(FileType(storage=FileSystemStorage(path="uploads")))
    role = Column(String, unique=False, nullable=False)

class UserInDB(Admin):
    password: Column(String, nullable=False)


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phoneno = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(ARRAY(JSON), nullable=True)
    active = Column(Boolean, unique=False, default=False)
    description = Column(String, nullable=False)
    
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    author = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    publishdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(FileType(storage=storage))
    ebook = Column(FileType(storage=storage))
    description = Column(String, nullable=False)

class Rating(Base):
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True, index=True)
    userId =  Column(Integer,nullable=False,index=True)
    bookId =  Column(Integer,nullable=False,index=True)
    rate = Column(Integer,nullable=False,index=True)

class BannerModel(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String,nullable=False)
    description = Column(String, nullable=False)
    postImage = Column(FileType(storage=storage))
    createdate = Column(DateTime, default=datetime.datetime.now)


class Library(Base):
    __tablename__ = "library"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    author = Column(String, nullable=False)
    createdate = Column(DateTime, default=datetime.datetime.now)
    publishdate = Column(DateTime, default=datetime.datetime.now)
    postImage = Column(FileType(storage=storage))
    description = Column(String, nullable=False)