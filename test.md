```mermaid
sequenceDiagram
    participant Frontend (Next.js)
    participant API_Gateway
    participant User_Service
    participant Product_Service
    
    Frontend->>API_Gateway: GET /api/users
    API_Gateway->>User_Service: GET /users
    User_Service-->>API_Gateway: User data
    API_Gateway-->>Frontend: User data
    
    Frontend->>API_Gateway: POST /api/products
    API_Gateway->>Product_Service: POST /products
    Product_Service-->>API_Gateway: Product created
    API_Gateway-->>Frontend: Product created
```