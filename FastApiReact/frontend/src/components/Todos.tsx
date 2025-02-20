import { Box, Button, Container, DialogActionTrigger, DialogBody, DialogContent, DialogFooter, DialogHeader, DialogRoot, DialogTitle, DialogTrigger, Flex, Input, Stack, Text } from "@chakra-ui/react";
import { ChangeEvent, createContext, FormEvent, useContext, useEffect, useState } from "react";

interface Todo {
  id: string;
  item: string;
}

const TodosContext = createContext({
  todos: [],
  fetchTodos: () => { },
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
        <AddTodo />
        <Stack gap={5}>
          {todos.map((todo: Todo) => (
            <TodoHelper item={todo.item} id={todo.id} fetchTodos={fetchTodos} />
          ))}
        </Stack>
      </Container>
    </TodosContext.Provider>
  );
};

const AddTodo = () => {
  const [item, setItem] = useState("");
  const { todos, fetchTodos } = useContext(TodosContext);

  const handleinput = (event: ChangeEvent<HTMLInputElement>) => {
    setItem(event.target.value);
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const newTodo = {
      "id": todos.length + 1,
      "item": item,
    }

    fetch("http://localhost:8000/todo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newTodo),
    }).then(fetchTodos);
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        pr='4.5rem'
        type='text'
        placeholder="add a todo item"
        aria-label="add a todo item"
        onChange={handleinput}
      />
    </form>
  )
}

interface UpdateTodoProps {
  item: string;
  id: string;
  fetchTodos: () => void;
}

const UpdateTodo = ({ item, id, fetchTodos }: UpdateTodoProps) => {

  const [todo, setTodo] = useState(item);

  const updateTodo = async () => {
    await fetch(`http://localhost:8000/todo/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item: todo })
    });
    await fetchTodos();
  };

  return (
    <DialogRoot>
      <DialogTrigger asChild>
        <Button h='1.5rem' size='sm'>
          update todo
        </Button>
      </DialogTrigger>
      <DialogContent
        position="fixed"
        top='50%'
        left='50%'
        transform="translate(-50%,-50%)"
        bg="white"
        p='6'
        rounded='sm'
        shadow='xl'
        maxW="md"
        w='90%'
        zIndex={1000}
      >

        <DialogHeader>
          <DialogTitle>update todo</DialogTitle>
        </DialogHeader>

        <DialogBody>
          <Input
            pr="4.5rem"
            type="text"
            placeholder="add todo item"
            aria-label="add todo item"
            value={todo}
            onChange={event => setTodo(event.target.value)}
          />
        </DialogBody>

        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="outline" size='sm'>Cancel</Button>
          </DialogActionTrigger>
          <DialogActionTrigger asChild>
            <Button size='sm' onClick={updateTodo}>Save</Button>
          </DialogActionTrigger>
        </DialogFooter>

      </DialogContent>
    </DialogRoot>
  )
};

interface TodoHelperProps {
  item: string;
  id: string;
  fetchTodos: () => void;
}

const TodoHelper = ({ id, item, fetchTodos }: TodoHelperProps) => {
  return (
    <Box p={1} shadow="sm">
      <Flex justify="space-between">
        <Text as="div" mt={4}>
          {item}
          <Flex align="end">
            <UpdateTodo item={item} id={id} fetchTodos={fetchTodos} />
            <DeleteTodo id={id} fetchTodos={fetchTodos}/>
          </Flex>
        </Text>
      </Flex>
    </Box>
  )
}

interface deleteTodoProps {
  id: string;
  fetchTodos: () => void;
}

const DeleteTodo = ({ id, fetchTodos }: deleteTodoProps) => {
  const deleteTodo = async () => {
    await fetch(`http://localhost:8000/todo/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id })
    });
    await fetchTodos();
  }

  return (<Button h="1.5rem" size='sm' marginLeft={2} onClick={deleteTodo}>Delete Todo</Button>);
}

export default Todos;
