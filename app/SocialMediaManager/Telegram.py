import asyncio
from typing import Dict, Tuple, Callable
from os import path

from config import TELEGRAM_OWNER_CHAT_ID, TELEGRAM_TOKEN
from app import logger_module

import aiogram


# This is used to keep track of videos that need human voice acting.
# { *message id*: [*path to video that needs audio*, *callback*] }
latest_audio_requests: Dict[int, Tuple[str, Callable[[str, str], None]]] = dict()
bot = aiogram.Bot(TELEGRAM_TOKEN)
dispatcher = aiogram.Dispatcher(bot)


async def run_bot() -> None:
    await dispatcher.start_polling()


async def ask_for_human_audio(path_to_video: str, callback: Callable[[str, str], None]) -> None:
    logger_module.logger.info(f"Asking for human voice acting for video: {path_to_video}")
    # Step 1. Send video
    stream = open(path_to_video, mode="rb")
    bot_message = await bot.send_video(TELEGRAM_OWNER_CHAT_ID, stream,
                                       caption="Reply on this message with voice acting")
    stream.close()
    # Step 2. Add message id to "order list" to get audio from reply message later
    latest_audio_requests[bot_message.message_id] = (path_to_video, callback, )


@dispatcher.message_handler(content_types=["voice"])
async def handle_voice_message(message: aiogram.types.Message):
    if message.chat.id != TELEGRAM_OWNER_CHAT_ID:
        await message.reply("Error! You are not owning this bot so you can't use it")
        return

    if message.reply_to_message is None:
        await message.reply("Error! To add voice on video reply on original message (**right click**)")
        return
    # Determining which video this audio message belongs to
    source_message = message.reply_to_message.message_id
    path_to_video, video_callback = latest_audio_requests.get(source_message, (None, None,))
    # Check if user replied on one of video messages
    if path_to_video is None:
        await message.reply("Error! To add audio **reply on video message**.\nTry again")
    else:
        logger_module.logger.info(f"Voice acting was submitted for video: {path_to_video}")
        # Downloading voice message as audio file
        file_info = await bot.get_file(message.voice.file_id)
        # This is a temp file which will be deleted later so it's location doesn't matter
        path_to_audio = path.abspath(f"human_audio_{message.message_id}.ogg")
        await bot.download_file(file_info.file_path, path_to_audio)

        video_callback(path_to_video=path_to_video, path_to_audio=path_to_audio)


@dispatcher.message_handler(commands="/stop")
async def stop_server(message: aiogram.types.Message):
    await dispatcher.stop_polling()
    await bot.close()


@dispatcher.message_handler(commands="/help")
async def help_message(message: aiogram.types.Message):
    # TODO: help
    await message.reply("")
