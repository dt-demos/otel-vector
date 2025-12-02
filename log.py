import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "log.source": record.filename
        }
        return json.dumps(log_data)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Set JSON formatter
file_handler.setFormatter(JSONFormatter())

# Add handler to logger
logger.addHandler(file_handler)

# Get command line argument or use default
message_suffix = sys.argv[1] if len(sys.argv) > 1 else ""

# Add an example log message
logger.info("This is an example log message written to app.log " + message_suffix)

print("Log message written to app.log in JSON format with log line content suffix:" + message_suffix)