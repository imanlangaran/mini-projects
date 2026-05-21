import { InMemoryUsersRepository } from "./frameworks/in-memory-users.repository";
import { CreateUserUseCase } from "./usecases/create-user.usecase";

const userRepository = new InMemoryUsersRepository();
const createUser = new CreateUserUseCase(userRepository);

createUser.execute({email: 'iman@gmail.com', password: 'hahahah'})
  .then(() => console.log("user created"))
  .catch((err) => console.log('there was an error:', err))
  // .catch(err => console.log('there was an error:', err))
