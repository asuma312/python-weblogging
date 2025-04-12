from enum import Enum


class LOGTYPES(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    CRITICAL = "critical"
    SUCCESS = "success"
    FAILURE = "failure"
    ALL = "all"
