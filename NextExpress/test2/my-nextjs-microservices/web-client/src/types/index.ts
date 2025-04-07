export interface User {
    id: string;
    name: string;
    email: string;
}

export interface AuthRequest {
    email: string;
    password: string;
}

export interface AuthResponse {
    token: string;
    user: User;
}

export interface UserRequest {
    id: string;
}

export interface UserResponse {
    user: User;
}