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

# Test full task lifecycle
def test_full_task_lifecycle(client):
    # Create
    create_response = client.post('/tasks', json={
        'title': 'Integration Task',
        'description': 'Testing full lifecycle'
    })
    assert create_response.status_code == 201
    task_id = create_response.get_json()['id']

    # Read
    get_response = client.get(f'/tasks/{task_id}')
    assert get_response.status_code == 200
    assert get_response.get_json()['title'] == 'Integration Task'

    # Update
    update_response = client.put(f'/tasks/{task_id}', json={
        'title': 'Updated Integration Task',
        'done': True
    })
    assert update_response.status_code == 200
    assert update_response.get_json()['done'] == True

    # Delete
    delete_response = client.delete(f'/tasks/{task_id}')
    assert delete_response.status_code == 200

    # Confirm deleted
    confirm_response = client.get(f'/tasks/{task_id}')
    assert confirm_response.status_code == 404

# Test multiple tasks
def test_multiple_tasks(client):
    client.post('/tasks', json={'title': 'Task 1'})
    client.post('/tasks', json={'title': 'Task 2'})
    client.post('/tasks', json={'title': 'Task 3'})

    response = client.get('/tasks')
    assert response.status_code == 200
    assert len(response.get_json()) == 3

# Test task completion workflow
def test_task_completion_workflow(client):
    # Create task
    response = client.post('/tasks', json={
        'title': 'Complete Me',
        'description': 'This task will be completed'
    })
    task_id = response.get_json()['id']

    # Verify not done
    task = client.get(f'/tasks/{task_id}').get_json()
    assert task['done'] == False

    # Mark as done
    client.put(f'/tasks/{task_id}', json={'done': True})

    # Verify done
    updated_task = client.get(f'/tasks/{task_id}').get_json()
    assert updated_task['done'] == True

# Test invalid task operations
def test_invalid_operations(client):
    # Get non-existent task
    response = client.get('/tasks/999')
    assert response.status_code == 404

    # Update non-existent task
    response = client.put('/tasks/999', json={'title': 'Ghost'})
    assert response.status_code == 404

    # Delete non-existent task
    response = client.delete('/tasks/999')
    assert response.status_code == 404

# Test health check with tasks present
def test_health_with_data(client):
    client.post('/tasks', json={'title': 'Task 1'})
    client.post('/tasks', json={'title': 'Task 2'})
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'