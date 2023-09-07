import math


# @see https://tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code.html
def apply_color_temperature(color, color_temperature) -> tuple:
    if color_temperature == 6600:
        return color

    factor_red = 255 if color_temperature <= 6600 \
        else 329.698727446 * ((color_temperature / 100 - 60) ** -0.1332047592)
    factor_green = 99.4708025861 * math.log(color_temperature / 100) - 161.1195681661 if color_temperature <= 6600 \
        else 288.1221695283 * ((color_temperature / 100 - 60) ** -0.0755148492)
    factor_blue = 255 if color_temperature >= 6600 else 0 if color_temperature <= 1900 \
        else 138.5177312231 * math.log(color_temperature / 100 - 10) - 305.0447927307

    factor_red = 0 if factor_red < 0 else 255 if factor_red > 255 else factor_red
    factor_green = 0 if factor_green < 0 else 255 if factor_green > 255 else factor_green
    factor_blue = 0 if factor_blue < 0 else 255 if factor_blue > 255 else factor_blue

    r, g, b = color
    return (
        r * (factor_red / 255.0),
        g * (factor_green / 255.0),
        b * (factor_blue / 255.0)
    )
