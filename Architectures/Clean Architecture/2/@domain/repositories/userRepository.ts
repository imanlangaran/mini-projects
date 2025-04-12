// @domain/repositories/userRepository.ts

import type { User } from '@domain/models/user';

// UserRepository port
export type UserRepository = {
  create(user: Omit<User, 'id'>): Promise<User>;
  findByEmail(email: string): Promise<User | null>;
};