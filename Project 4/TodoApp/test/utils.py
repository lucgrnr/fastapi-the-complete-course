from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

# Code that is used for all tests is added here

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}
    # important to be an admin for many of the tests

"""
To avoid changing all the app endpoints and make it easier to write tests, 
you can use dependency injection to override dependencies in your tests. 
This approach allows you to provide custom implementations of dependencies without modifying the actual application code.
"""

client = TestClient(app)

# Create a single todo then delete it in order to run our tests
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1, # matches with our current user id
    )
    # Adding the User to the Database:
    db = TestingSessionLocal() # A new TestingSessionLocal session is created.
    db.add(todo) # The user object is added to the session using db.add(user).
    db.commit() # The session is committed to save the user to the database using db.commit().

    # Yielding the User Object:
    yield todo 
    # The yield keyword is used to return the user object to the test function. 
    # This allows the test function to use the user object in its assertions.
    
    # Tearing Down the User:
    # After the test function completes, the fixture automatically runs the code after the yield statement.
    with engine.connect() as connection: # A connection to the database is established using engine.connect().
        connection.execute(text("DELETE FROM todos;")) # SQL statement is executed to remove all users from the database.
        connection.close()
        connection.commit() # The connection is committed to ensure that the changes are saved.

# Create a single user then delete it in order to run our tests
@pytest.fixture
def test_user():
    user = Users(
        username="codingwithrobytest",
        email="codingwithrobytest@email.com",
        first_name="Eric",
        last_name="Roby",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

# FIXTURE
# The purpose of this fixture is to provide a clean and isolated test user for each test function that needs to interact with the user model. 
# By setting up the user before the test runs and tearing it down afterward, 
# you ensure that each test starts with a clean database state and does not interfere with other tests.

# This approach helps in isolating the tests and making them more reliable and easier to maintain. 
# It ensures that each test is run in a controlled environment where the database state is consistent and predictable.

# YIELD
# Generators and Yield
# When you define a function with a yield statement, it becomes a generator function. 
# A generator function is a special type of function that can pause its execution and return a value to the caller, 
# but it can also resume execution from where it left off when called again.

# Yield in Pytest Fixtures
# In the context of pytest, a fixture is a function that is used to set up and tear down test environments. 
# When you use yield in a fixture, the function behaves in a specific way:

# - Setup Phase: The code before the yield statement is executed during the setup phase of the test. 
# This is where you set up any necessary resources, such as creating test data or initializing a database connection.

# - Test Phase: The yield statement is a special marker that tells pytest to pause the execution of the fixture and pass control back to the test function. 
# The test function receives the value yielded by the fixture.

# - Teardown Phase: After the test function completes, the code after the yield statement is executed during the teardown phase of the test. 
# This is where you clean up any resources, such as deleting test data or closing a database connection.


