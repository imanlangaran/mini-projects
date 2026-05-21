import { User } from "../entities/user.entity";

export interface UserRepository {
  save(user : User): Promise<void>;
}