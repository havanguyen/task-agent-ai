# System Design

## Architecture Overview

```mermaid
graph TB
    subgraph Client
        Web[Web Browser]
        Agent[AI Agent CLI]
    end
    
    subgraph Docker["Docker Compose"]
        Nginx[Nginx :80]
        
        subgraph Backend["Backend Service"]
            FastAPI[FastAPI :8000]
            MCP[MCP Server]
        end
        
        Postgres[(PostgreSQL :5432)]
        Redis[(Redis :6379)]
    end
    
    subgraph External
        Gemini[Google Gemini API]
    end
    
    Web --> Nginx
    Nginx --> FastAPI
    Agent --> FastAPI
    Agent --> Gemini
    FastAPI --> Postgres
    FastAPI --> Redis
    MCP --> FastAPI
```

## Component Details

### 1. Nginx (Reverse Proxy)
- **Port**: 80
- **Role**: Load balancing, SSL termination, static file serving
- Routes all `/api` requests to FastAPI backend

### 2. FastAPI Backend
- **Port**: 8000 (internal)
- **Features**:
  - RESTful API endpoints
  - JWT Authentication
  - Role-based Access Control (RBAC)
  - Swagger UI documentation (`/docs`)
  - Health check endpoint (`/health`)

### 3. PostgreSQL Database
- **Port**: 5432
- **Role**: Primary data storage
- **Tables**: Organization, User, Project, Task, Comment, Attachment, Notification

### 4. Redis
- **Port**: 6379
- **Role**: Caching, session storage, notification queue

### 5. MCP Server
- Auto-discovers FastAPI routes
- Exposes all endpoints as MCP tools
- Used by AI Agent for tool execution

### 6. AI Agent
- Uses Google Gemini for natural language understanding
- Calls MCP tools via HTTP
- Interactive CLI for task management

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Nginx
    participant FastAPI
    participant DB as PostgreSQL
    participant Cache as Redis
    
    User->>Nginx: HTTP Request
    Nginx->>FastAPI: Proxy Request
    FastAPI->>FastAPI: JWT Validation
    FastAPI->>DB: Query/Mutation
    DB-->>FastAPI: Result
    FastAPI->>Cache: Cache Update
    FastAPI-->>Nginx: JSON Response
    Nginx-->>User: HTTP Response
```

## AI Agent Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as AI Agent
    participant Gemini as Google Gemini
    participant API as FastAPI
    
    User->>Agent: Natural Language Request
    Agent->>Gemini: Interpret Request
    Gemini-->>Agent: Tool Selection + Params
    Agent->>API: Execute Tool (HTTP)
    API-->>Agent: Result
    Agent->>Gemini: Summarize Result
    Gemini-->>Agent: Natural Language Response
    Agent-->>User: Display Response
```

## Security

- **Authentication**: JWT tokens with configurable expiration
- **Authorization**: Role-based (Admin, Manager, Member)
- **Password**: Bcrypt hashing
- **CORS**: Configurable origins
- **File Uploads**: Size limit (5MB), count limit (3 per task)

## Scaling Considerations

- **Horizontal**: Multiple FastAPI instances behind Nginx
- **Database**: PostgreSQL connection pooling
- **Caching**: Redis for frequently accessed data
- **Files**: External storage (S3) for attachments in production
