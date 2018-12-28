import datetime
import settings


def log_print(message, message_type=2):
    if message_type <= settings.LOG_LEVEL:
        now = datetime.datetime.now()
        print(f"[{now}]: {message}")
