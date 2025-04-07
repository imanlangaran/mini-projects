export interface User {
    id: string;
    name: string;
    email: string;
}

export interface UserResponse {
    user: User;
    message: string;
}