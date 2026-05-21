import { User } from "../entities/user.entity";
import { UserRepository } from "../interfaces/users.repository";

export class InMemoryUsersRepository implements UserRepository {
  private users: User[]= [];

  async save(user: User): Promise<void> {
    this.users.push(user);
  }
}