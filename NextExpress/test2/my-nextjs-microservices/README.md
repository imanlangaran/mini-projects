# my-nextjs-microservices/README.md

# My Next.js Microservices Project

This project is a simple web application built with Next.js, utilizing a microservice architecture. It consists of two main services: an authentication service and a user service, along with a web client that interacts with these services.

## Project Structure

```
my-nextjs-microservices
├── services
│   ├── auth-service
│   ├── user-service
├── web-client
├── docker-compose.yml
└── README.md
```

## Services

### Auth Service

- **Path:** `services/auth-service`
- **Description:** This service handles authentication-related requests. It includes endpoints for user login, registration, and token management.

### User Service

- **Path:** `services/user-service`
- **Description:** This service manages user-related functionalities, including user profile management and user data retrieval.

## Web Client

- **Path:** `web-client`
- **Description:** The web client is built with Next.js and serves as the frontend for the application. It communicates with the auth and user services to provide a seamless user experience.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-nextjs-microservices
   ```

2. **Install dependencies for each service and the web client:**
   ```bash
   cd services/auth-service
   npm install
   cd ../user-service
   npm install
   cd ../../web-client
   npm install
   ```

3. **Run the application using Docker Compose:**
   ```bash
   docker-compose up
   ```

4. **Access the web client:**
   Open your browser and navigate to `http://localhost:3000`.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.