from os import path

from app.Video.video_config import SOURCE_PATH, FPS, RESULT_PATH

from PIL import Image, ImageFont, ImageDraw
import moviepy.editor as mpe
from moviepy.audio.fx.audio_loop import audio_loop


def load_image(filename: str, mode="RGB") -> Image.Image:
    return Image.open(path.join(SOURCE_PATH, filename)).convert(mode)


def load_font(filename: str, size=24) -> ImageFont.ImageFont:
    return ImageFont.truetype(path.join(SOURCE_PATH, filename), size=size)


def draw_text(surface: Image.Image, text: str, font: ImageFont.ImageFont,
              color=(240, 240, 240), center_x=True, center_y=True) -> None:
    draw = ImageDraw.ImageDraw(surface)
    text_size = draw.textsize(text, font)
    text_pos = [(surface.size[0] - text_size[0] * int(center_x)) / 2,
                (surface.size[1] - text_size[1] * int(center_y)) / 2]
    draw.text(text_pos, text, color, font)


def animate_text_typing(text: str, font: ImageFont.ImageFont, background_image: Image.Image,
                        global_frame_counter: int, char_limit_for_new_line: int,
                        frame_duration: float = 1 / (FPS * 0.5), sound_volume_modifier=0.3,
                        typing_sound_path=path.join(SOURCE_PATH, "text_typing.mp3"),
                        text_color=(240, 240, 240), text_center_x=True, text_center_y=True) -> mpe.VideoClip:
    # TODO: individual sound for each char (duration for ImageClip will be the same as sound length).
    #  This also will make sound for new line better.
    #  Source: https://www.fesliyanstudios.com/royalty-free-sound-effects-download/keyboard-typing-6 (Single Button)

    # TODO: also support for multiline text
    frame_path_format_string = path.join(RESULT_PATH, "frames", "{0:05}.png")
    start_frame_num = global_frame_counter
    # Step 1. Generate frames
    for i in range(-1, len(text)):
        current_frame = background_image.copy()

        draw_text(current_frame, text[:i + 1], font, text_color, text_center_x, text_center_y)

        current_frame.save(frame_path_format_string.format(global_frame_counter))
        global_frame_counter += 1
    # Step 2. Create clip from generated frames
    clip = mpe.concatenate_videoclips([mpe.ImageClip(frame_path_format_string.format(i)).set_duration(frame_duration)
                                       for i in range(start_frame_num, global_frame_counter)],
                                      method="compose")
    # Step 3. Add looping audio to clip
    clip = clip.set_audio(audio_loop(mpe.AudioFileClip(typing_sound_path),
                                     duration=clip.duration))
    clip = clip.volumex(sound_volume_modifier)
    return clip
