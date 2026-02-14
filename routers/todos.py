from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from typing import Annotated

from database import SessionDep
from models import Todo

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/todos", response_class=HTMLResponse)
def create_todo(request: Request, title: Annotated[str, Form()], session: SessionDep):
    todo = Todo(title=title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return templates.TemplateResponse("partials/todo_item.html", {"request": request, "todo": todo})

@router.patch("/todos/{todo_id}", response_class=HTMLResponse)
def toggle_todo(request: Request, todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        return HTMLResponse(status_code=404)
    todo.completed = not todo.completed
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return templates.TemplateResponse("partials/todo_item.html", {"request": request, "todo": todo})

@router.delete("/todos/{todo_id}", response_class=HTMLResponse)
def delete_todo(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        return HTMLResponse(status_code=404)
    session.delete(todo)
    session.commit()
    return HTMLResponse(status_code=200)
