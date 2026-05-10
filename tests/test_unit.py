import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test health endpoint
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'

# Test get all tasks - empty
def test_get_tasks_empty(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    assert response.get_json() == []

# Test create task
def test_create_task(client):
    response = client.post('/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'
    assert data['done'] == False

# Test create task without title
def test_create_task_no_title(client):
    response = client.post('/tasks', json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()

# Test get single task
def test_get_single_task(client):
    client.post('/tasks', json={'title': 'Single Task'})
    response = client.get('/tasks/1')
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Single Task'

# Test update task
def test_update_task(client):
    client.post('/tasks', json={'title': 'Old Title'})
    response = client.put('/tasks/1', json={'title': 'New Title', 'done': True})
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'New Title'
    assert data['done'] == True

# Test delete task
def test_delete_task(client):
    client.post('/tasks', json={'title': 'To Delete'})
    response = client.delete('/tasks/1')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Task deleted'

# Test get deleted task
def test_get_deleted_task(client):
    client.post('/tasks', json={'title': 'To Delete'})
    client.delete('/tasks/1')
    response = client.get('/tasks/1')
    assert response.status_code == 404