from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field
from starlette import status # starlette installed automatically with FastAPI
# important imports!
app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

# Use this class for data validation
class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None) # find_book_id function will create the id
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6) # greater than / less than
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                'published_date': 2029
            }
        }
    }
     
""""
In FastAPI, validation is primarily handled by Pydantic models. 
You define a Pydantic model with specific field constraints and then use that model as a type hint in your endpoint function parameters. 
FastAPI will automatically parse the incoming request data and validate it against the Pydantic model.

Understanding model_config
model_config is a configuration dictionary that can be added to a Pydantic model to customize its behavior. Some common keys include:
- allow_population_by_field_name: Allows field population by field name.
- extra: Specifies how to handle extra fields (e.g., ignore, allow, or forbid).
- validate_assignment: Enables or disables validation when setting fields.
In your case, you're using json_schema_extra to add an example to the model's JSON schema.

Why Use model_config with json_schema_extra?
Improved Documentation: By providing an example payload, the API documentation becomes more user-friendly and informative. Users can see a sample of the expected JSON structure when interacting with the API.
Validation Guidance: The example serves as a reference for the expected data format, guiding users on how to structure their requests correctly.
Developer Convenience: Having a clear example reduces the likelihood of user errors when interacting with the API, as they can refer to the documentation for guidance.

"""


BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)): # Path is used to validate Path parameters
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')

"""
These two endpoints do not interfere with each other because FastAPI (built on Starlette) evaluates routing path structure and trailing slashes distinctly, separating path parameters from query parameters.

1. Explicit Trailing Slash vs. Exact Segment Path
@app.get("/books/{book_id}"): Matches paths with two path segments (e.g., /books/1, /books/42).
@app.get("/books/"): Matches the base collection path with a trailing slash (e.g., /books/).

2. Path Parameter vs. Query Parameter Handling
In read_book, book_id is defined as a Path parameter (/books/{book_id}). When a request comes to /books/15, FastAPI routes 15 as book_id.
In read_book_by_rating, book_rating is a Query parameter (book_rating: int = Query(...)). The URL path remains strictly /books/, and the parameter is passed via the query string:
GET /books/?book_rating=5
"""

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)): # Query is used to validate Query parameters
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

"""
While using a BookRequest class can encapsulate validation logic, 
it is not always necessary or practical to define a separate class for each endpoint's parameters. 
The Query decorator in FastAPI provides a convenient way to validate and parse query parameters directly within the function signature.

Using a class for validation would lead to much longer code:
class BookRequest:
    def __init__(self, book_rating: int):
        self.book_rating = book_rating

    @property
    def book_rating(self):
        return self._book_rating

    @book_rating.setter
    def book_rating(self, value):
        if not (0 < value < 6):
            raise ValueError("Book rating must be between 1 and 5")
        self._book_rating = value

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int):
    try:
        book_request = BookRequest(book_rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    books_to_return = []
    for book in BOOKS:
        if book["rating"] == book_request.book_rating:
            books_to_return.append(book)
    return books_to_return
"""


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest): # must be of type BookRequest
    new_book = Book(**book_request.model_dump()) # transform into Book object
    BOOKS.append(find_book_id(new_book))
"""
book_request.model_dump(): This method converts the validated Pydantic model instance into a dictionary.
Book(**book_request.model_dump()): This creates a new Book instance by unpacking the dictionary into the Book constructor.
find_book_id(new_book): This function assigns a unique ID to the new book. If the BOOKS list is empty, the ID is set to 1. Otherwise, the ID is set to one more than the last book's ID in the list.
BOOKS.append(find_book_id(new_book)): The new book is added to the BOOKS list.
"""

def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed: # without this, the app could return code 200 even if it doesn't do anything
        raise HTTPException(status_code=404, detail='Item not found')
# note: no response Body for a 204

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
