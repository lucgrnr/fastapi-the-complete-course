from fastapi import Body, FastAPI

app = FastAPI()


BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

# IMPORTANT: All endpoints should be different
# FastAPI does not automatically redirect between paths with and without trailing slashes. 
# Instead, it treats them as distinct paths. 
# This means that the following two endpoints are different and will handle requests independently:
#@app.get("/books")
#@app.get("/books/")

@app.get("/")
async def welcome():
    return {"Welcome!"}

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book


@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# Get all books from a specific author using path or query parameters
@app.get("/books/byauthor/") # query approach
# @app.get("/books/byauthor/{author}") # path approach
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return

"""
IMPORTANT:

Why Order Matters:
Specific Routes First: More specific routes (e.g., those with path parameters) should be defined before more general routes. This ensures that the request is matched to the most specific route available.
Avoid Ambiguity: If a request can match multiple routes, FastAPI will execute the first one it encounters. Defining specific routes first helps avoid unintended behavior due to route ambiguity.

@app.get("/books/byauthor/{author}"): This route matches requests to /books/byauthor/AuthorName. It is more specific because it uses a path parameter.
@app.get("/books/{book_author}/"): This route matches requests to /books/AuthorName/CategoryName/. It is more general because it uses both path parameters.

Best Practices:
Define Specific Routes First: Always define routes with specific path parameters before more general routes.
Use Descriptive Names: Ensure that your route names are descriptive and intuitive to avoid confusion.
Document Your API: Maintain clear documentation of your API endpoints to help users understand how to interact with your application.
"""

@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return

# IMPORTANT: app.get do not support body information

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    # Pass the book information in the Body of the request
    # Here we append the json Body as is


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
        # we match the title for the update here
            BOOKS[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
        # again, we match on the title for the deletion
            BOOKS.pop(i)
            break
