from PIL import ImageStat
import math


def get_brightness(im, br_mode, color):
    if br_mode == "dominant":
        r, g, b = color
        return (r + g + b) / 3

    if br_mode == "natural":
        stat = ImageStat.Stat(im)
        r, g, b = stat.mean
        return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))

    if br_mode == "rms":
        stat = ImageStat.Stat(im.convert('L'))
        return stat.rms[0]

    # mean
    stat = ImageStat.Stat(im.convert('L'))
    return stat.mean[0]
