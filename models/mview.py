from sqladmin import Admin, ModelView
from models.model import Admin,Student,Book,Rating,BannerModel,Library,Borrow

class AdminView(ModelView, model=Admin):
    column_list = [Admin.id, Admin.username, Admin.role,Admin.active,Admin.createdate,Admin.postImage]
    icon = "fa-solid fa-user-circle"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class StudentView(ModelView, model=Student):
    column_list = [Student.id, Student.username, Student.active]
    icon = "fa-solid fa-user"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class BookView(ModelView, model=Book):
    column_list = [Book.id, Book.name, Book.category, Book.author,Book.publisher,Book.publishdate,Book.postImage,Book.ebook]
    icon = "fa-solid fa-book"
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    can_edit = False


class RatingView(ModelView, model=Rating):
    column_list = [Rating.id,Rating.userId, Rating.bookId,Rating.rate]
    icon = "fa-solid fa-thumbs-up"
    page_size = 50
    page_size_options = [25, 50, 100, 200]

class BannerView(ModelView, model=BannerModel):
    name = "Banner"
    name_plural = "Banners"
    column_list = [BannerModel.id,BannerModel.title, BannerModel.description,BannerModel.postImage]
    icon = "fa-solid fa-television"
    page_size = 50
    page_size_options = [25, 50, 100, 200]


class LibraryView(ModelView, model=Library):
    column_list = [Library.id, Library.name, Library.quantity,Library.createdate,Library.postImage]
    icon = "fa-solid fa-id-card"
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    can_edit = False

class BorrowView(ModelView, model=Borrow):
    column_list = [Borrow.id, Borrow.username, Borrow.bookname,Borrow.createdate,Borrow.confirm]
    icon = "fa-solid fa-address-book"
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    can_edit = True