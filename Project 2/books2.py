from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field
from starlette import status

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
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return



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
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


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
