"""Constants for the ambient_extractor component."""
DOMAIN = "ambient_extractor"
SERVICE_TURN_ON = "turn_on"

# Image sources
ATTR_PATH = "ambient_extract_path"
ATTR_URL = "ambient_extract_url"

# Brightness
ATTR_BRIGHTNESS_AUTO = "brightness_auto"
ATTR_BRIGHTNESS_MODE = "brightness_mode"
ATTR_BRIGHTNESS_MIN = "brightness_min"
ATTR_BRIGHTNESS_MAX = "brightness_max"

# Image cropping
# left offset in % of source width
ATTR_CROP_X = "crop_left"
# right offset in % of source height
ATTR_CROP_Y = "crop_top"
# width in % of source width, 0 means full image
ATTR_CROP_W = "crop_width"
# height in % of source height, 0 means full image
ATTR_CROP_H = "crop_height"

# Color temperature
ATTR_COLOR_TEMPERATURE = "color_temperature"


