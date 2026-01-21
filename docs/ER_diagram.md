# Entity Relationship Diagram

## Database Schema

```mermaid
erDiagram
    Organization ||--o{ User : has
    Organization ||--o{ Project : owns
    
    User ||--o{ Task : "assigned to"
    User ||--o{ Comment : writes
    User ||--o{ Notification : receives
    User }o--o{ ProjectMember : "belongs to"
    
    Project ||--o{ Task : contains
    Project ||--o{ ProjectMember : has
    
    Task ||--o{ Comment : has
    Task ||--o{ Attachment : has

    Organization {
        int id PK
        string name UK
    }
    
    User {
        int id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        enum role "admin/manager/member"
        int organization_id FK
    }
    
    Project {
        int id PK
        string name
        text description
        int organization_id FK
    }
    
    ProjectMember {
        int project_id PK,FK
        int user_id PK,FK
    }
    
    Task {
        int id PK
        string title
        text description
        enum status "todo/in-progress/done"
        enum priority "low/medium/high"
        datetime due_date
        int project_id FK
        int assignee_id FK
        datetime created_at
        datetime updated_at
    }
    
    Comment {
        int id PK
        text content
        int task_id FK
        int user_id FK
        datetime created_at
    }
    
    Attachment {
        int id PK
        string filename
        string file_path
        int task_id FK
        datetime uploaded_at
    }
    
    Notification {
        int id PK
        string title
        text message
        boolean is_read
        int user_id FK
        datetime created_at
    }
```

## Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| Organization → User | One-to-Many | An organization has many users |
| Organization → Project | One-to-Many | An organization has many projects |
| Project → Task | One-to-Many | A project contains many tasks |
| Project ↔ User | Many-to-Many | Users can be members of multiple projects (via ProjectMember) |
| Task → User | Many-to-One | A task is assigned to one user |
| Task → Comment | One-to-Many | A task can have many comments |
| Task → Attachment | One-to-Many | A task can have max 3 attachments |
| User → Notification | One-to-Many | A user receives many notifications |

## Indexes

- `organization.name` - Unique index
- `user.email` - Unique index
- `user.organization_id` - Foreign key index
- `project.organization_id` - Foreign key index
- `task.project_id` - Foreign key index
- `task.assignee_id` - Foreign key index
- `task.status` - Index for filtering
