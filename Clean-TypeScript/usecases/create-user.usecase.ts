import { User } from "../entities/user.entity";
import { UserRepository } from "../interfaces/users.repository";

interface CreateUserRequest {
  email: string;
  password: string;
}

export class CreateUserUseCase {
  constructor(private userRepository: UserRepository) { }

  async execute(request: CreateUserRequest) : Promise<void> {
    const user = User.create(request.email, request.password);
    await this.userRepository.save(user);
  }
}