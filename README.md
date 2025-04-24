# APScheduler-Admin

A comprehensive task scheduling management system based on APScheduler, with FastAPI backend and Ant Design Vue 3 frontend.

## Features

- **Task Management**: Create, edit, delete, pause, resume, and execute tasks
- **Multiple Trigger Types**: Support for cron, interval, and date triggers
- **Task Logs**: View task execution logs and results
- **User Management**: User authentication and authorization with JWT
- **Multi-Database Support**: Compatible with MySQL and PostgreSQL
- **Docker Support**: Easy deployment with Docker Compose
- **Responsive UI**: Modern and user-friendly interface with Ant Design Vue 3

## System Architecture

### Backend Technology Stack

- **FastAPI**: High-performance asynchronous Python web framework
- **APScheduler**: Python task scheduling library
- **SQLAlchemy**: ORM framework for database operations
- **Pydantic**: Data validation and settings management
- **JWT**: For user authentication
- **Alembic**: Database migration tool

### Frontend Technology Stack

- **Vue 3**: Frontend framework
- **Ant Design Vue**: UI component library
- **Vite**: Build tool
- **Pinia**: State management
- **Vue Router**: Routing management
- **Axios**: HTTP client

### Database Support

- **MySQL**: Using PyMySQL as the driver
- **PostgreSQL**: Using psycopg2 as the driver

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL or PostgreSQL

### Installation and Setup

#### Option 1: Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/williamhatch/APScheduler-Admin.git
   cd APScheduler-Admin
   ```

2. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api/v1

#### Option 2: Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/williamhatch/APScheduler-Admin.git
   cd APScheduler-Admin
   ```

2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Configure the .env file with your database settings
   # Start the backend server
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   
   # Start the frontend development server
   npm run dev
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/v1

### Initial Login

- Username: `admin`
- Password: `admin`

## API Documentation

After starting the backend server, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

### Users Table

- id: Primary key
- username: Username
- hashed_password: Hashed password
- email: Email address
- is_active: Whether the user is active
- is_superuser: Whether the user is a superuser
- created_at: Creation time
- updated_at: Update time

### Jobs Table

- id: Primary key
- name: Job name
- func: Job function
- args: Job arguments
- kwargs: Job keyword arguments
- trigger: Trigger type (cron, interval, date)
- trigger_args: Trigger arguments
- max_instances: Maximum number of instances
- next_run_time: Next run time
- misfire_grace_time: Misfire grace time
- coalesce: Whether to coalesce
- status: Job status (running, paused)
- description: Job description
- created_at: Creation time
- updated_at: Update time
- created_by: Creator ID

### Job Logs Table

- id: Primary key
- job_id: Job ID
- status: Execution status (success, failed)
- start_time: Start time
- end_time: End time
- duration: Execution duration
- error_message: Error message
- output: Output information

## Project Structure

```
APScheduler-Admin/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   ├── tests/
│   ├── .env
│   ├── alembic.ini
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── store/
│   │   ├── utils/
│   │   └── views/
│   ├── .env
│   ├── .env.production
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [APScheduler](https://github.com/agronholm/apscheduler) - Advanced Python Scheduler
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Vue.js](https://vuejs.org/) - Progressive JavaScript Framework
- [Ant Design Vue](https://antdv.com/) - UI Component Library for Vue.js
