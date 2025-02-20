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
    {"id": 1, "item": "description"},
    {"id": 2, "item": "description"},
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
    
@app.put("/todo/{id}", tags=['todos'])
async def update_todos(id:int, body:dict) -> dict:
    for todo in todos:
        if(todo['id'] == id):
            todo['item'] = body['item']
            return {
                'data' : f"todo with id {id} has been updated",
            }
    return {
        "data": f"todo with id {id} not found",
    }
    
@app.delete('/todo/{id}', tags=['todos'])
async def delete_todo(id:int) -> dict :
    for todo in todos:
        if(todo['id'] == id) :
            todos.remove(todo)
            return {
                "data": f"Todo with id {id} removed",
            }
    return {
        "data" : f"Todo with id {id} not found",
    }