import { Container, Stack } from "@chakra-ui/react";
import { createContext, useEffect, useState } from "react";

interface Todo {
  id: string;
  item: string;
}

const TodosContext = createContext({
  todos: [],
  fetchTodos: () => {},
});

const Todos = () => {
  const [todos, setTodos] = useState([]);

  const fetchTodos = async () => {
    const response = await fetch("http://localhost:8000/todos");
    const data = await response.json();
    setTodos(data.data);
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <TodosContext.Provider value={{ todos, fetchTodos }}>
      <Container maxW="container.xl" pt="100px">
        <Stack gap={5}>
          {todos.map((todo: Todo) => (
            <b key={todo.id}>{todo.item}</b>
          ))}
        </Stack>
      </Container>
    </TodosContext.Provider>
  );
};

export default Todos;
