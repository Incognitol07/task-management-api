# Task Management API

The **Task Management API** enables users to manage and automate tasks, including creating, updating, and scheduling reminders. With support for recurring tasks, automated notifications, and secure user authentication, this API helps users efficiently manage their daily tasks.

## Problem Solved

Managing tasks can be overwhelming without an efficient system. This API simplifies task management by allowing users to:

- **Create, update, and delete tasks**: Organize tasks with important details and statuses.
- **Automate task reminders**: Receive reminders for tasks through scheduled notifications.
- **Manage recurring tasks**: Set up tasks that repeat at specified intervals.
- **Secure user access**: Log in and manage tasks with JWT-based authentication.

## Key Features

- **User Management**: Register, log in, and authenticate users with JWT-based authentication.
- **Task Management**: Add, update, and delete tasks, including assigning deadlines and priorities.
- **Recurring Tasks**: Automate the creation of recurring tasks using a task scheduler.
- **Task Reminders**: Set reminders for tasks and automate notification delivery.
- **Real-time Notifications**: Receive notifications for upcoming tasks.
- **Secure Access**: Protect user data and tasks with secure JWT authentication.
- **Automation**: Use Celery or Python's `schedule` library for task automation.

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication
- **Task Scheduling**: Celery / Python `schedule`
- **Notifications**: Email or in-app notification system
- **Deployment**: Heroku / Docker

---

## Installation

### Prerequisites  

- **Python 3.12+**  
- **PostgreSQL** (for primary database setup)  
- **Docker** (if deploying via Docker)  

### Installation Steps  

#### 1. Clone the Repository  

```bash  
git clone https://github.com/Incognitol07/task-management-api
cd task-management-api
```  

#### 2. Set Up Virtual Environment  

1. **Create the virtual environment**:  

   ```bash  
    python -m venv venv  
   ```  

2. **Activate the virtual environment**:  

   - **Windows**:  

     ```cmd  
     .\venv\Scripts\activate  
     ```  

   - **Linux/Mac**:  

     ```bash  
     source venv/bin/activate  
     ```  

3. **Install dependencies**:  

   ```bash  
   pip install -r requirements.txt  
   ```  

4. **Deactivate the virtual environment (when done)**:  

   ```bash  
   deactivate  
   ```  

---

#### 3. Set Up Environment Variables  

Create a `.env` file:  

- **Linux/Mac**:  

  ```bash  
  cp .env.example .env  
  ```  

- **Windows**:  

  ```cmd  
  copy .env.example .env  
  ```  

Edit the `.env` file and provide the required configuration:  

```plaintext  
ENVIRONMENT=development  
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>  
JWT_SECRET_KEY=your_secret_key  
```  

---

### Database Setup  

#### Using PostgreSQL  

1. Create a database in your PostgreSQL instance.  
2. Update the `DATABASE_URL` in your `.env` file with the database details.  

#### Optional: Using SQLite  

1. Modify the `.env` file:  

   ```plaintext
   DATABASE_URL=sqlite:///purple_laundry.db  
   ```  

2. No additional setup is required for SQLite.  

---

### Running the Application  

#### With Docker  

1. **Build and run the container**:  

   ```bash  
   docker-compose up --build  
   ```  

2. The API will be available at `http://127.0.0.1:8000`.  

3. **Stop the container**:  

   ```bash  
   docker-compose down  
   ```  

#### Without Docker  

1. **Activate the virtual environment**:  

   ```bash  
   source venv/bin/activate  # Use appropriate command based on your OS  
   ```  

2. **Start the server**:  

   ```bash  
   uvicorn app.main:app --reload  
   ```  

3. Visit `http://127.0.0.1:8000` in your browser.  

---

## Features Overview

### Task Management

- **Create, Update, Delete Tasks**: Add, update, or delete tasks with details such as title, description, due date, and status.
- **Task Reminders**: Set reminders for tasks based on due dates and receive notifications via email or in-app notifications.
- **Recurring Tasks**: Set up recurring tasks with intervals (e.g., daily, weekly, monthly).

### Automation and Scheduling

- **Task Automation**: Automate task reminders using Celery or Python's `schedule` library.
- **Recurring Tasks Endpoint**: Create an endpoint to manage recurring tasks with automation logic to schedule them at specific intervals.

### Real-time Notifications

- **Email or In-App Notifications**: Receive notifications for upcoming tasks and reminders.

---

## Project Structure

```plaintext
task-management-api/
├── app/
│   ├── main.py              # Application entry point
│   ├── routers/             # API endpoint routers
│   ├── schemas/             # Pydantic models for request validation
│   ├── utils/               # Utility functions (e.g., scheduling, notifications)
│   ├── models/              # SQLAlchemy models
│   ├── database.py          # Database connection and session handling
│   └── config.py            # Configuration settings
├── requirements.txt         # Versions of installed packages
├── docker-compose.yml       # Docker Compose configuration for the app and database
├── Dockerfile               # Dockerfile for building the web service image
├── .env                     # Environment variables
└── README.md                # Project documentation
```

---

## Testing the API

You can test the API using **curl**, **Postman**, or FastAPI's interactive docs available at <http://127.0.0.1:8000/docs>.

### Example Request

To create a new task:

```bash
curl -X POST "http://127.0.0.1:8000/tasks" -H "accept: application/json" -H "Content-Type: application/json" -d '{"title": "Test Task", "description": "Test task description", "due_date": "2024-12-31T23:59:59"}'
```

### Scheduling a Recurring Task

To create a recurring task:

```bash
curl -X POST "http://127.0.0.1:8000/recurring-tasks" -H "accept: application/json" -H "Content-Type: application/json" -d '{"title": "Recurring Task", "interval": "daily"}'
```

---

## Conclusion

The **Task Management API** provides a robust system for managing tasks, automating reminders, and scheduling recurring tasks. With secure user authentication, task management, and automation tools, this API enables efficient and organized task management for individuals and teams.

## License

This project is licensed under the MIT License.
