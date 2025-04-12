# SDK LogSQL

## Overview
This SDK now provides integration via WebSockets for interaction with the LogSQL service.

## Módulo

- **SDK_WS**: Contém classes e handlers para comunicação WebSocket, incluindo gerenciamento de conexão e autenticação.

## Uso

### WebSocket
```python
from pyweblog import SetupLogger
import logging
logger = SetupLogger(
    name="your_logger",
    username="your_user",
    password="your_password",
    level=logging.DEBUG
)
```

You can pass the Bearer token as well
```python
from pyweblog import SetupLogger
import logging
logger = SetupLogger(
    name="your_logger",
    token="your_api_token",
    level=logging.DEBUG
)
```

## Final Considerations
This SDK was developed to facilitate integration with the LogSQL service through asynchronous communication using WebSockets.This SDK was developed to 

## Description

This project provides a simple way to log and manage SQL queries. It ensures safer data handling and helps developers track query execution.

## Features

• Easy to integrate into existing projects  
• Real-time logging  
• Configurable output options  

## Installation

1. Clone the repository  
2. Run the setup script  
3. Configure the logging options  

## Usage

Call the logger function in your SQL-related scripts, passing your query string. The query is automatically recorded.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss future improvements.

## License

MIT
`