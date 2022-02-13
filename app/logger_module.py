import sys
import logging

import coloredlogs

from config import LOGGER_STYLES


class LoggerWrapper(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)

    def error(self, msg, *args, **kwargs) -> None:
        """Logs error message, notifies about this message and exits app"""
        super().error(msg, *args, **kwargs)
        # TODO: notifying logic here for any error
        sys.exit(1)


# __name__ value doesn't matter since whole app uses one logger
logging.setLoggerClass(LoggerWrapper)
logger = logging.getLogger(__name__)


def init() -> None:
    """Add colors and other configurations to logger"""
    coloredlogs.install(level=logging.DEBUG, logger=logger,
                        fmt="[%(asctime)s] %(levelname)s: %(message)s",
                        field_styles=LOGGER_STYLES["FIELD"],
                        level_styles=LOGGER_STYLES["LEVEL"])