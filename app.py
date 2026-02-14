import uvicorn
from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated, Optional

# --- Database Setup ---
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    completed: bool = False

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# --- App Setup ---
app = FastAPI(title="ToDo App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: SessionDep):
    todos = session.exec(select(Todo)).all()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

@app.post("/todos", response_class=HTMLResponse)
def create_todo(request: Request, title: Annotated[str, Form()], session: SessionDep):
    todo = Todo(title=title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    # Return just the new todo item HTML fragment for HTMX to append
    return templates.TemplateResponse("partials/todo_item.html", {"request": request, "todo": todo})

@app.patch("/todos/{todo_id}", response_class=HTMLResponse)
def toggle_todo(request: Request, todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        return HTMLResponse(status_code=404)
    todo.completed = not todo.completed
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return templates.TemplateResponse("partials/todo_item.html", {"request": request, "todo": todo})

@app.delete("/todos/{todo_id}", response_class=HTMLResponse)
def delete_todo(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        return HTMLResponse(status_code=404)
    session.delete(todo)
    session.commit()
    return HTMLResponse(status_code=200) # HTMX will remove the element

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
