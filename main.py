import asyncio

from config import Config, LOGGER_STYLES
from app import StackOverFlow, logger_module
from app.SocialMediaManager import TikTok, Telegram
from app.Video import generator as video_generator


# Parsing config from CLI
config: Config = Config.from_cli_args()


async def main(loop):
    logger_module.init(LOGGER_STYLES, notify_owner_on_error=not config.debug)
    # Starting Telegram bot
    # Note: Not using await because this for some reason block the loop
    loop.create_task(Telegram.run_bot())

    while Telegram.dispatcher.loop.is_running():
        # Step 1. Parse questions
        for question in StackOverFlow.parse_questions(config.questions_amount):
            # Step 2. Generate video for every single question
            await video_generator.process_video_creation(config, question,
                                                         on_video_ready_callback=on_video_ready_handler)
        await asyncio.sleep(config.scheduler_delay_sec)


def on_video_ready_handler(path_to_video: str) -> None:
    TikTok.upload_video(config.tiktok_cookies_path, config.chromedriver_path,
                        path_to_video)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main(event_loop))
