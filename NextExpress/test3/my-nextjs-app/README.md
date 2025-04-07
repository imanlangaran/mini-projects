# My Next.js Microservices App

This project is a simple web application built with Next.js that utilizes a microservice architecture. It consists of two main services: an authentication service and a user service, along with a web application that interacts with these services.

## Project Structure

```
my-nextjs-app
├── services
│   ├── auth-service       # Authentication microservice
│   ├── user-service       # User management microservice
├── web                    # Next.js web application
├── docker-compose.yml     # Docker configuration for services
└── README.md              # Project documentation
```

## Services

### Auth Service

- **Path:** `services/auth-service`
- **Description:** This service handles user authentication, including login and registration.
- **Entry Point:** `services/auth-service/src/index.ts`
- **Types:** Defined in `services/auth-service/src/types/index.ts`

### User Service

- **Path:** `services/user-service`
- **Description:** This service manages user data and profiles.
- **Entry Point:** `services/user-service/src/index.ts`
- **Types:** Defined in `services/user-service/src/types/index.ts`

## Web Application

- **Path:** `web`
- **Description:** The frontend application built with Next.js that communicates with the microservices.
- **Main Entry Point:** `web/pages/index.tsx`
- **Global Styles:** Defined in `web/styles/globals.css`

## Getting Started

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd my-nextjs-app
   ```

2. **Install dependencies for services:**
   - Navigate to each service directory and run:
     ```
     npm install
     ```

3. **Install dependencies for the web application:**
   ```
   cd web
   npm install
   ```

4. **Run the application using Docker:**
   ```
   docker-compose up
   ```

## Usage

- Access the web application at `http://localhost:3000`.
- The web app will communicate with the auth and user services to handle authentication and user data.

## License

This project is licensed under the MIT License.