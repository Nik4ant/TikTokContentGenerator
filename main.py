import asyncio

from config import Config, LOGGER_STYLES
from app import logger_module
from app.SocialMediaManager import Telegram


# Parsing config from CLI
config: Config = Config.from_cli_args()


def main():
    logger_module.init(LOGGER_STYLES, notify_owner_on_error=not config.debug)
    # Starting Telegram bot
    # Telegram.run_bot()

    logger_module.logger.info("End of main")


if __name__ == '__main__':
    main()
