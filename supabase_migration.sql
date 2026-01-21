-- Supabase Migration Script
-- Run this in Supabase SQL Editor

-- Organization table
CREATE TABLE IF NOT EXISTS organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_organization_id ON organization(id);
CREATE INDEX IF NOT EXISTS ix_organization_name ON organization(name);

-- Project table
CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organization(id)
);
CREATE INDEX IF NOT EXISTS ix_project_id ON project(id);
CREATE INDEX IF NOT EXISTS ix_project_name ON project(name);

-- User table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR DEFAULT 'member',
    organization_id INTEGER NOT NULL REFERENCES organization(id)
);
CREATE INDEX IF NOT EXISTS ix_user_id ON "user"(id);
CREATE INDEX IF NOT EXISTS ix_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS ix_user_full_name ON "user"(full_name);

-- Notification table
CREATE TABLE IF NOT EXISTS notification (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_notification_id ON notification(id);

-- Project Member table
CREATE TABLE IF NOT EXISTS project_member (
    project_id INTEGER NOT NULL REFERENCES project(id),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    PRIMARY KEY (project_id, user_id)
);

-- Task table
CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'todo',
    priority VARCHAR DEFAULT 'medium',
    due_date TIMESTAMP,
    project_id INTEGER NOT NULL REFERENCES project(id),
    assignee_id INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_task_id ON task(id);
CREATE INDEX IF NOT EXISTS ix_task_title ON task(title);

-- Attachment table
CREATE TABLE IF NOT EXISTS attachment (
    id SERIAL PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    task_id INTEGER NOT NULL REFERENCES task(id),
    uploaded_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_attachment_id ON attachment(id);

-- Comment table
CREATE TABLE IF NOT EXISTS comment (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    task_id INTEGER NOT NULL REFERENCES task(id),
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_comment_id ON comment(id);

-- Alembic version table (for tracking migrations)
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version (version_num) VALUES ('50f09d0ca8bd') ON CONFLICT DO NOTHING;
