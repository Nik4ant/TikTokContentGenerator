from os import path, listdir

from app.StackOverFlow import Question
from app.logger_module import logger
# Local imports
from app.Video.video_config import RESULT_PATH, FPS
import app.Video.utils as utils

import moviepy.editor as mpe


test_question = Question("python",
                         "What does if __name__ == \"__main__\": do?",
                         open("app/Video/data/source/test.html").read(),
                         "https://stackoverflow.com/questions/419163/what-does-if-name-main-do",
                         "419163")


def create_video(question: Question = test_question) -> str:
    """
    Generates video by given question
    :return: Path to generated video
    """
    logger.info("Generating video")
    final_video_clips = []
    global_frame_counter = 0

    # Background for whole video
    background_image = utils.load_image("background.png")
    # Question title
    title_font = utils.load_font("SyneTactile.ttf")
    final_video_clips.append(utils.animate_text_typing(question.title, title_font, background_image,
                                                       global_frame_counter, None))
    # Final video
    path_to_video = path.abspath(path.join(RESULT_PATH, "result.mp4"))
    mpe.concatenate_videoclips(final_video_clips).write_videofile(path_to_video, fps=FPS)

    logger.info(f"Video for question {question.id} generated: {path_to_video}")
    return path_to_video
