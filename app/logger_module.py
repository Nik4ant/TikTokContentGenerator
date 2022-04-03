import sys
import logging

from app import SocialMediaManager
from config import TELEGRAM_OWNER_CHAT_ID

import coloredlogs


class LoggerWrapper(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        # If true bot will DM owner if something goes wrong (default False)
        # Note: No way to init it here so this var is set in init function below
        self.notify_owner_on_error = False

    def error(self, msg, *args, **kwargs) -> None:
        """Logs error message, notifies about this message and exits app"""
        super().error(msg, *args, **kwargs)
        if self.notify_owner_on_error or True:
            exc_type, exc_value, exc_traceback = kwargs.get("exc_info", (None, None, None, ))
            message_html = msg
            # Check if there was exception or this is just an error message
            # TODO:
            if exc_type is not None:
                pass
            else:
                pass
            # Notifying about error
            telegram_loop = SocialMediaManager.Telegram.dispatcher.loop
            telegram_loop.create_task(SocialMediaManager.Telegram.bot.send_message(TELEGRAM_OWNER_CHAT_ID, message_html,
                                                                                   parse_mode="html"))
        sys.exit(1)


# __name__ value doesn't matter since whole app uses one logger
logging.setLoggerClass(LoggerWrapper)
logger = logging.getLogger(__name__)


def init(logger_styles: dict, notify_owner_on_error: bool = False) -> None:
    """Add colors and do other logger configuration"""
    sys.excepthook = handle_exception
    logger.notify_owner_on_error = notify_owner_on_error
    coloredlogs.install(level=logging.DEBUG, logger=logger,
                        fmt="[%(asctime)s] %(levelname)s: %(message)s",
                        field_styles=logger_styles["field_styles"],
                        level_styles=logger_styles["level_styles"])
    logger.info("Logger module initiated")


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
