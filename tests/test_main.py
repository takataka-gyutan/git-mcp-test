from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest
from app import app, get_session, Todo

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "My Tasks" in response.text

def test_create_todo(client: TestClient):
    response = client.post("/todos", data={"title": "Test Task"})
    assert response.status_code == 200
    assert "Test Task" in response.text
    
    # Verify DB state
    todos = client.get("/")
    assert "Test Task" in todos.text

def test_toggle_todo(client: TestClient):
    # Setup
    client.post("/todos", data={"title": "Task to Toggle"})
    
    response = client.patch("/todos/1")
    assert response.status_code == 200
    assert "completed" in response.text

def test_delete_todo(client: TestClient):
    # Setup
    client.post("/todos", data={"title": "Task to Delete"})
    
    response = client.delete("/todos/1")
    assert response.status_code == 200
