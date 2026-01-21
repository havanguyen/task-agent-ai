# Setup virtual environment
setup:
    python3 -m venv venv
    . venv/bin/activate && pip install -r requirements.txt

# Run local development server
run:
    . venv/bin/activate && uvicorn app.main:app --reload

# Run via Docker
docker-build:
    docker-compose build

docker-up:
    docker-compose up

docker-down:
    docker-compose down

# Database Migrations
migrate:
    . venv/bin/activate && alembic upgrade head

migrate-create msg:
    . venv/bin/activate && alembic revision --autogenerate -m "{{msg}}"

# Testing
test:
    . venv/bin/activate && pytest -v

# MCP Server
mcp:
    . venv/bin/activate && python3 app/mcp/server.py

# Agent
agent:
    . venv/bin/activate && python3 app/agent/agent.py

agent-test:
    . venv/bin/activate && python3 app/agent/agent.py test

frontend-setup:
    cd frontend && npm install

frontend-dev:
    cd frontend && npm run dev

frontend-build:
    cd frontend && npm run build
