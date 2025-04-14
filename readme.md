# LogSQL

## Description

LogSQL is a web application developed with Flask and Flask-SocketIO to manage logs and user authentication. It uses SQLite for log storage and provides both HTTP endpoints and WebSocket events for account creation, log management, and authentication. Log databases are stored in a subfolder for each user, enabling more efficient reads and inserts.

## Features

- User account creation and authentication.
- Password recovery through passkeys.
- Log insertion and querying via REST and WebSocket.
- Validation and filtering of logs with various types and filters.

## How to Use

1. **Environment Setup**  
   - Install the dependencies:  
     ```
     pip install -r requirements.txt
     ```
   - Configure the environment variables in a `.env` file. Define parameters such as `USERS_LOGDB_PATH`, `JWT_SECRET_TOKEN`, `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY`, `BASE_SELECT_LOGS`, and `LIMIT_SELECT_LOGS`.

2. **Running the Application**  
   - Run the main file:  
     ```
     python app.py
     ```
   - The application will start on host `0.0.0.0` and port `1234`.

3. **HTTP Endpoints and WebSocket Events**  
   - **HTTP Endpoints:**  
     - `/api/v1/auth/create_account` – Creates a new user account.
     - `/api/v1/auth/forgot_password` – Recovers a user's password.
     - `/api/v1/auth/request_token` – Requests a new access token.
     - `/api/v1/logs/insert_log` – Inserts a log.
     - `/api/v1/logs/select_logs` – Queries logs.

   - **WebSocket Events:**  
     - `create_account` – Creates a user account via socket.
     - `forgot_password` – Updates the password via socket.
     - `login` and `logout` – Handle authentication via socket.
     - `insert_log`, `insert_multiple_logs`, `select_logs`, and `get_log` – Handle logs via socket.

## Project Structure

- **app.py:** Application configuration and initialization for Flask and SocketIO.
- **routes/**: Contains HTTP endpoints for authentication and log management.
- **events/**: Defines SocketIO events for real-time communication.
- **models/**: Data models including the user definition and database configuration.
- **utils/**: Helper functions for log manipulation and path management.

## Python client
You can find python client both in pypi: https://pypi.org/project/pythonweblog-client-ws/
And in github repo: https://github.com/asuma312/pyweblog_client


## Final Considerations

This project is suited for applications requiring centralized log management and robust authentication, integrating both synchronous (HTTP) and asynchronous (WebSocket) communication.
