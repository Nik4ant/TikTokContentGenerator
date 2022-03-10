from os import path, remove
from random import choice

from config import VIDEO_STATIC_PATH

import moviepy.editor as mpe
from PIL import Image, ImageFont, ImageDraw
from moviepy.audio.fx.audio_loop import audio_loop


TYPING_SOUNDS = {
    # TODO: maybe faster sounds? (idk)
    "basic": [
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_1.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_2.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_3.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_4.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_5.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_6.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_7.mp3")),
        mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_8.mp3")),
    ],
    # TODO: Need better sounds. Current one is working, but sucks
    # " ": [
    #     mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_space_1.mp3")),
    #   mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_space_2.mp3")),
    # ],
    # "\n": [
    #     mpe.AudioFileClip(path.join(VIDEO_STATIC_PATH, "typing_enter_1.mp3")),
    # ]
}


def load_image(filename: str, mode="RGB") -> Image.Image:
    return Image.open(path.join(VIDEO_STATIC_PATH, filename)).convert(mode)


def load_font(filename: str, size=24) -> ImageFont.ImageFont:
    return ImageFont.truetype(path.join(VIDEO_STATIC_PATH, filename), size=size)


def draw_text(surface: Image.Image, text: str, font: ImageFont.ImageFont,
              color=(240, 240, 240), center_x=True, center_y=True) -> None:
    draw = ImageDraw.ImageDraw(surface)
    text_size = draw.textsize(text, font)
    text_pos = [(surface.size[0] - text_size[0] * int(center_x)) / 2,
                (surface.size[1] - text_size[1] * int(center_y)) / 2]
    draw.text(text_pos, text, color, font)


def animate_text_typing(text: str, font: ImageFont.ImageFont, background_image: Image.Image,
                        char_limit_for_new_line: int, sound_volume_modifier=0.14, frame_duration_modifier=0.75,
                        text_color=(240, 240, 240), text_center_x=True, text_center_y=True) -> mpe.VideoClip:
    # TODO: char_limit_for_new_line multiline support? (not sure if this is a good place to handle this)
    result_clips = []
    # File will be deleted anyway so it's location doesn't matter
    current_temp_frame_path = path.abspath("temp_frame.png")
    # Step 1. Generate frames
    for i in range(-1, len(text)):
        current_frame = background_image.copy()
        draw_text(current_frame, text[:i + 1], font, text_color, text_center_x, text_center_y)
        current_frame.save(current_temp_frame_path)
        # Random typing sound for each char
        current_sound = choice(TYPING_SOUNDS.get(text[i], TYPING_SOUNDS["basic"]))
        frame_duration = current_sound.duration
        result_clips.append(mpe.ImageClip(current_temp_frame_path)
                            .set_audio(mpe.CompositeAudioClip([current_sound]))
                            .set_duration(frame_duration * frame_duration_modifier))
    # Deleting file used for temp frame
    remove(current_temp_frame_path)
    # Step 2. Create clip from generated frames
    clip = mpe.concatenate_videoclips(result_clips, method="compose")
    clip = clip.volumex(sound_volume_modifier)

    return clip
