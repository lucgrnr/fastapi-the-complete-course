from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Todos
from .utils import * # import everything

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

"""
The dependency_overrides variable is a dictionary in FastAPI that allows you to override the dependencies for your routes during testing. 
It comes from the fastapi module.

Definition:
dependency_overrides is a dictionary that maps dependencies to their overridden versions.
This dictionary is a property of the FastAPI application instance (app).

Usage:
You can override dependencies in the dependency_overrides dictionary during testing to provide custom implementations.
This allows you to control the behavior of dependencies without modifying the actual application code.
"""

def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}


def test_read_one_authenticated_not_found():
    response = client.get("/todo/999") # should fail because this todo number does not exist
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    # Used to retrieve the newly created todo item from the database and verify that it has been created correctly
    # Issues with the Current Approach:
    # Hardcoded ID: The test function assumes that a todo with ID 2 already exists in the database. This is not a robust approach.
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change the title of the todo already saved!'


def test_update_todo_not_found(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}













