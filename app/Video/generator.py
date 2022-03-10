from typing import Callable
from os import path, listdir, remove

from config import Config
from app.StackOverFlow import Question
from app.logger_module import logger
from app.SocialMediaManager import Telegram
import app.Video.utils as utils

import moviepy.editor as mpe


async def process_video_creation(config: Config, question: Question, on_video_ready_callback: Callable[[str], None]):
    def merge_video_and_audio(path_to_video: str, path_to_audio: str):
        logger.info(f"Applying audio: {path_to_audio} to video: {path_to_video}")
        # Merging audio with video
        video = mpe.VideoFileClip(path_to_video)
        audio = mpe.AudioFileClip(path_to_audio)
        # Note(Nik4ant): Have no idea why it works, but it works
        # TODO: fix audio overwriting (currently voice acting overrides rest of the audio)
        composed_audio = mpe.CompositeAudioClip([audio, video.audio])
        video.audio = composed_audio
        # Writing final video
        final_video_path = path.join(config.video_result_path, f"{question.id}.mp4")
        video.write_videofile(final_video_path, logger=None)
        # Deleting temp content used for current video
        remove(path_to_audio)
        remove(path_to_video)
        on_video_ready_callback(final_video_path)

    logger.info(f"Generating video for question: {question.id}")
    final_video_clips = []
    # Background for whole video
    background_image = utils.load_image("background.png")

    # Question title
    title_font = utils.load_font("RobotoMono.ttf")
    final_video_clips.append(utils.animate_text_typing(question.title, title_font, background_image, None))

    # Final video
    no_voice_video_path = path.join(config.video_result_path, f"no_voice_question_{question.id}.mp4")
    mpe.concatenate_videoclips(final_video_clips).write_videofile(no_voice_video_path, fps=config.video_fps,
                                                                  logger=None)

    logger.info(f"Video for question {question.id} generated: {no_voice_video_path}")
    await Telegram.ask_for_human_audio(no_voice_video_path, callback=merge_video_and_audio)
