import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.logger import logger
from models.schema import (
    CurrentUser,BookReviewSchema,BorrowSchema

)
from typing import List, Dict
from .database import get_db

from sqlalchemy.orm import Session
from modules.dependency import get_current_user
from modules.token import AuthToken
from sqlalchemy import desc

from models.model import  Student as User
from models.model import Book,Rating,BannerModel,Library,Borrow
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from modules.utils import pagination
router = APIRouter()
auth_handler = AuthToken()



@router.get("/profiles/{id}", tags=["library"])
def get_profile(id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    profile_data = db.get(User, current_user["id"])
    if not profile_data:
        raise HTTPException(status_code=404, detail="User ID not found.")
    return {"profile":profile_data}


@router.get("/banners", tags=["banner"])
async def get_app_banners(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db)#, current_user: CurrentUser = Depends(get_current_user)
):
    banners = db.query(BannerModel).order_by(desc(BannerModel.createdate)).all()
    return {"banner":banners}

@router.get("/libraries", tags=["library"])
async def get_libs(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(Library).count()
    meta_data =  pagination(page,per_page,count)
    book = db.query(Library).order_by(desc(Library.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"library":book}


@router.get("/libraries/{id}", tags=["library"])
def get_lib_byid(id: int, db: Session = Depends(get_db)):
    book_data = db.get(Library, id)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book ID not found.")
    return {"library":book_data}


@router.post("/borrow", tags=["books"])
async def borrow_book(
    request: Request, data: BorrowSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(data.dict())
    book_data = db.get(Library, data.book_id)
    print(book_data)
    print(current_user)
    book_id = data.book_id
    user_id = current_user["id"]
    is_borrowed = db.query(Borrow).filter(Borrow.userId==user_id,Borrow.bookId==book_id).first()
    if is_borrowed:
        return {"status":"Already made request"}
    else:
        borrow_db = Borrow(username=current_user["username"],userId=current_user["id"],bookId=book_id,bookname=book_data.name,description="borrow")
        db.add(borrow_db)
        db.commit()
        db.refresh(borrow_db)
        return {"status":"Sent Borrow Request"}
    return {}

@router.get("/books", tags=["books"])
async def get_book_categories(
    page: int = 1 , per_page: int=10,
    db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    count = db.query(Book).count()
    meta_data =  pagination(page,per_page,count)
    book = db.query(Book).order_by(desc(Book.createdate)).limit(per_page).offset((page - 1) * per_page).all()
    return {"book":book}

@router.get("/books/{id}", tags=["books"])
def get_book_byid(id: int, db: Session = Depends(get_db)):
    book_data = db.get(Book, id)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book ID not found.")
    return {"book":book_data}

@router.post("/add_review", tags=["books"])
async def add_review(
    request: Request, data: BookReviewSchema, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    logger.info(data.dict())
    req = data.dict()
    book_rate  = int(req["rating"] * 2)
    book_id = req["book_id"]
    user_id = current_user["id"]
    print(book_rate)
    is_rating = db.query(Rating).filter(Rating.userId==user_id,Rating.bookId==book_id).first()
    if is_rating:
        is_rating.rate = book_rate
        db.commit()
        db.refresh(is_rating)
        return {"status":"update","rating":req["rating"]}
    else:
        rating_db = Rating(userId=current_user["id"],bookId=book_id,rate=book_rate)
        db.add(rating_db)
        db.commit()
        db.refresh(rating_db)
        return {"status":"create","rating":req["rating"]}


@router.get("/get_review/{book_id}", tags=["books"])
def get_review(book_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    is_rating = db.query(Rating).filter(Rating.userId==current_user["id"],Rating.bookId==book_id).first()
    if not is_rating:
        return {"rating":0}
    print(is_rating.rate)
    return {"rating":is_rating.rate/2}


def get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix, num_recommendations=5):
    """
    Get top recommendations for a given user.
    """
    user_ratings = session.query(Rating).filter_by(userId=user_id).all()
    rated_books = [rating.bookId for rating in user_ratings]
    unrated_books_indices = [i for i, book in enumerate(all_books) if book.id not in rated_books]
    user_ratings_vector = ratings_matrix[user_id, :]  # Get the user's ratings vector
    user_similarity_scores = cosine_similarity([user_ratings_vector], ratings_matrix)[0]  # Compute similarity scores
    user_sim_scores_sum = np.sum(user_similarity_scores)  # Sum of similarity scores
    sorted_indices = np.argsort(user_similarity_scores)[::-1]  # Sort indices in descending order
    recommended_books_indices = [index for index in sorted_indices if index in unrated_books_indices][:num_recommendations]
    recommendations = [all_books[index] for index in recommended_books_indices]
    return recommendations


@router.get("/recommendations", tags=["predict"])
async def get_recom(
   session: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)
):
    user_id = current_user["id"]
    print(user_id)
    all_books = session.query(Book).all()
    num_books = len(all_books)
    num_users = session.query(User).count()
    ratings_matrix = np.zeros((num_users+1, num_books+1))
    print(ratings_matrix)
    print(num_users)
    print(num_books)
    print(session.query(Rating).count())
    for rating in session.query(Rating).all():
        try:
            print(ratings_matrix[rating.bookId , rating.userId ])
            ratings_matrix[rating.bookId , rating.userId ] = rating.rate
        except:
            pass
        print(ratings_matrix)
    cosine_similarity_matrix = cosine_similarity(ratings_matrix.T, ratings_matrix.T)
    recommendations = get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix)
    return {"recommendations":recommendations}


@router.get("/predict/{id}", tags=["predict"])
async def get_predict(
   id:int, session: Session = Depends(get_db)
):
    user_id = id
    all_books = session.query(Book).all()
    num_books = len(all_books)
    num_users = session.query(User).count()
    ratings_matrix = np.zeros((num_users+1, num_books+1))
    for rating in session.query(Rating).all():
        ratings_matrix[rating.bookId , rating.userId ] = rating.rate
    cosine_similarity_matrix = cosine_similarity(ratings_matrix.T, ratings_matrix.T)
    recommendations = get_recommendations_for_user(session, user_id, all_books, ratings_matrix, cosine_similarity_matrix)
    print("Recommendations for user with ID", user_id)
    for book in recommendations:
        print(book.name)
    return recommendations

