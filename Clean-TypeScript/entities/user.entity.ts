import { v4 as uuid } from 'uuid';

export class User {
  constructor(
    id: string,
    public email: string,
    public password: string
  ) { }

  static create(email: string, password: string) {
    const id = uuid();
    return new User(id, email, password)
  }
}