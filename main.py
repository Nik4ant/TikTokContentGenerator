import os
import sys

from app import logger_module
# TODO: rethink structure because currently usage looks weird: video_uploader.upload_video()
#  So maybe:
#  a) make TikTok.py with all stuff in it
#  b) rename to video_uploader.upload()
from app.TikTok import video_uploader


def main():
    video_uploader.upload_video()

    logger_module.logger.info("Done")


if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.curdir))
    logger_module.init()
    try:
        main()
    except Exception as e:
        logger_module.logger.error("Unhandled exception occurred", exc_info=e)
