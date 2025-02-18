from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

todos = [
    {"id": '1', "item": "description"},
    {"id": '2', "item": "description"},
]


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}


@app.get("/todos", tags=["todos"])
async def read_todos() -> dict:
    return {"data": todos}

@app.post("/todo" , tags=["todos"])
async def add_todo(todo: dict) -> dict:
    todos.append(todo)
    return {
        "data": "Todo added"
    }