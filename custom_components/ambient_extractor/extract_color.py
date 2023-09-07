from tempfile import TemporaryFile
from colorthief import ColorThief
from PIL import Image
import math


def get_file(file_path):
    """Get a PIL acceptable input file reference.

    Allows us to mock patch during testing to make BytesIO stream.
    """
    return file_path


def get_cropped_image(file_handler, crop_area):
    im = Image.open(file_handler)
    if crop_area['active']:
        im_width, im_height = im.size
        im = im.crop((
            math.floor(im_width / 100 * crop_area['x']),
            math.floor(im_height / 100 * crop_area['y']),
            math.floor(im_width / 100 * (crop_area['x'] + crop_area['w'])),
            math.floor(im_width / 100 * (crop_area['y'] + crop_area['h'])),
        ))
    return im


def get_color_from_image(im) -> tuple:
    file_handler = TemporaryFile()
    im.save(file_handler, "PNG")
    return get_color_from_file(file_handler)


def get_color_from_file(file_handler) -> tuple:
    """Given an image file, extract the predominant color from it."""
    color_thief = ColorThief(file_handler)

    # get_color returns a SINGLE RGB value for the given image
    color = color_thief.get_color(quality=1)
    return color


