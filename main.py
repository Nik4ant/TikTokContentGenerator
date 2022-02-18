import os
import sys


sys.path.append(os.path.abspath(os.curdir))


from app import logger_module, TikTok, StackOverFlow
from app.Video import generator


def main():
    generator.create_video()
    # TikTok.upload_video()

    logger_module.logger.info("Done")


if __name__ == '__main__':
    logger_module.init()
    try:
        main()
    except Exception as e:
        logger_module.logger.error("Unhandled exception occurred", exc_info=e)
