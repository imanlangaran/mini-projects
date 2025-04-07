// This file exports types and interfaces related to the user service.

export interface UserRequest {
    id: string;
    name: string;
    email: string;
}

export interface UserResponse {
    success: boolean;
    data?: User;
    error?: string;
}

export interface User {
    id: string;
    name: string;
    email: string;
    createdAt: Date;
    updatedAt: Date;
}