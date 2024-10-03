import pytest
from flask_jwt_extended import create_access_token
from src.app import create_app  # Assuming src/app.py is where your create_app is
from src.models import db
from src.models import User, Type, Occupation

# Fixture to create the app instance
@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for tests
    app.config['JWT_SECRET_KEY'] = '648ab73217495df79ebc3270ebae5893'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

# Fixture to provide a test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture to create JWT token for testing
@pytest.fixture
def token(app):
    with app.app_context():
        access_token = create_access_token(identity='admin')
        return access_token

# Helper function to create a user with permissions
def create_user_with_permissions(app, permissions):
    with app.app_context():
        user = User(username="testuser", password_hash="hashedpassword", permissions=permissions)
        db.session.add(user)
        db.session.commit()

# Test creating customer with new occupation and type
def test_create_customer_new_occupation_type(client, token, app):
    create_user_with_permissions(app, {"create_customers": "RW"})

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Define new customer with new occupation and type
    payload = {
        "customer_name": "New Customer",
        "occupation_name": "New Occupation",
        "type_name": "New Type"
    }

    # POST request to create a new customer
    response = client.post('/api/v1/customers', json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert data['data'][0]['customer_name'] == "New Customer"

# Test creating customer with existing occupation and type
def test_create_customer_existing_occupation_type(client, token, app):
    create_user_with_permissions(app, {"create_customers": "RW"})

    # Set up existing occupation and type
    with app.app_context():
        existing_type = Type(type_name="Existing Type")
        existing_occupation = Occupation(occupation_name="Existing Occupation")
        db.session.add(existing_type)
        db.session.add(existing_occupation)
        db.session.commit()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Define new customer with existing occupation and type
    payload = {
        "customer_name": "Customer With Existing Data",
        "occupation_name": "Existing Occupation",
        "type_name": "Existing Type"
    }

    response = client.post('/api/v1/customers', json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert data['data'][0]['customer_name'] == "Customer With Existing Data"

# Test creating customer with similar occupation and type (using Levenshtein distance)
def test_create_customer_similar_occupation_type(client, token, app):
    create_user_with_permissions(app, {"create_customers": "RW"})

    # Set up existing occupation and type to be similar to the new input
    with app.app_context():
        existing_type = Type(type_name="Developer")
        existing_occupation = Occupation(occupation_name="Engineer")
        db.session.add(existing_type)
        db.session.add(existing_occupation)
        db.session.commit()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Define customer with slightly different occupation and type (typo simulation)
    payload = {
        "customer_name": "Customer With Typo",
        "occupation_name": "Engneer",  # Similar to "Engineer"
        "type_name": "Devloper"        # Similar to "Developer"
    }

    response = client.post('/api/v1/customers', json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()

    # Assert that the typo was corrected by the Levenshtein logic
    assert 'data' in data
    assert data['data'][0]['occupation_name'] == "Engineer"
    assert data['data'][0]['type_name'] == "Developer"

# Test creating customer with insufficient permissions
def test_create_customer_insufficient_permissions(client, token, app):
    create_user_with_permissions(app, {"create_customers": "R"})  # Read-only permission

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Attempt to create a customer with insufficient permissions
    payload = {
        "customer_name": "Customer With Insufficient Permissions",
        "occupation_name": "Unauthorized Occupation",
        "type_name": "Unauthorized Type"
    }

    response = client.post('/api/v1/customers', json=payload, headers=headers)
    
    assert response.status_code == 403
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'User has insufficient permissions for this endpoint/method'

