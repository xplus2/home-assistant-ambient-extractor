"""Module for ambient_extractor (RGB/brightness extraction from images) component."""
import asyncio
import io
import logging

from PIL import UnidentifiedImageError, Image, ImageStat
import aiohttp
import async_timeout
from colorthief import ColorThief
import voluptuous as vol
import math
from tempfile import TemporaryFile

from homeassistant.components.light import (
    ATTR_RGB_COLOR,
#   ATTR_BRIGHTNESS_PCT,
    ATTR_BRIGHTNESS,
    DOMAIN as LIGHT_DOMAIN,
    LIGHT_TURN_ON_SCHEMA,
)
from homeassistant.const import SERVICE_TURN_ON as LIGHT_SERVICE_TURN_ON
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_PATH,
    ATTR_URL,
    DOMAIN,
    SERVICE_TURN_ON,

    ATTR_BRIGHTNESS_AUTO,
    ATTR_BRIGHTNESS_MODE,
    ATTR_BRIGHTNESS_MIN,
    ATTR_BRIGHTNESS_MAX,

    ATTR_CROP_X,
    ATTR_CROP_Y,
    ATTR_CROP_W,
    ATTR_CROP_H,
)

_LOGGER = logging.getLogger(__name__)

# Extend the existing light.turn_on service schema
SERVICE_SCHEMA = vol.All(
    cv.has_at_least_one_key(ATTR_URL, ATTR_PATH),
    cv.make_entity_service_schema(
        {
            **LIGHT_TURN_ON_SCHEMA,
            vol.Exclusive(ATTR_PATH, "ambient_extractor"): cv.isfile,
            vol.Exclusive(ATTR_URL, "ambient_extractor"): cv.url,
            vol.Optional(ATTR_BRIGHTNESS_AUTO, default=False): cv.boolean,
            vol.Optional(ATTR_BRIGHTNESS_MODE, default="mean"): cv.string,
            vol.Optional(ATTR_BRIGHTNESS_MIN, default=2): cv.positive_int,
            vol.Optional(ATTR_BRIGHTNESS_MAX, default=70): cv.positive_int,

            vol.Optional(ATTR_CROP_X, default=0): cv.positive_int,
            vol.Optional(ATTR_CROP_Y, default=0): cv.positive_int,
            vol.Optional(ATTR_CROP_W, default=0): cv.positive_int,
            vol.Optional(ATTR_CROP_H, default=0): cv.positive_int,

        }
    ),
)


def _get_file(file_path):
    """Get a PIL acceptable input file reference.

    Allows us to mock patch during testing to make BytesIO stream.
    """
    return file_path


def _get_color_from_image(im) -> tuple:
    file_handler = TemporaryFile()
    im.save(file_handler, "PNG")
    return _get_color_from_file(file_handler)


def _get_color_from_file(file_handler) -> tuple:
    """Given an image file, extract the predominant color from it."""
    color_thief = ColorThief(file_handler)

    # get_color returns a SINGLE RGB value for the given image
    color = color_thief.get_color(quality=1)
    _LOGGER.debug("Extracted RGB color %s from image", color)
    return color


def _get_cropped_image(file_handler, crop_area):
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


def _get_brightness(im, br_mode, color):
    if br_mode == "dominant":
        r, g, b = color
        return (r + g + b) / 3

    if br_mode == "natural":
        stat = ImageStat.Stat(im)
        r,g,b = stat.mean
        return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))

    if br_mode == "rms":
        stat = ImageStat.Stat(im.convert('L'))
        return stat.rms[0]

    # mean
    stat = ImageStat.Stat(im.convert('L'))
    return stat.mean[0]


async def async_setup(hass: HomeAssistant, hass_config: ConfigType) -> bool:
    """Set up services for ambient_extractor integration."""

    async def async_handle_service(service_call: ServiceCall) -> None:
        """Decide which ambient_extractor method to call based on service."""
        service_data = dict(service_call.data)

        br_min = 2
        br_max = 70
        check_brightness = True
        br_mode = "mean"
        if ATTR_BRIGHTNESS_MIN in service_data:
            br_min = service_data.pop(ATTR_BRIGHTNESS_MIN)
        if ATTR_BRIGHTNESS_MAX in service_data:
            br_max = service_data.pop(ATTR_BRIGHTNESS_MAX)
        if ATTR_BRIGHTNESS_AUTO in service_data:
            check_brightness = service_data.pop(ATTR_BRIGHTNESS_AUTO)
        if ATTR_BRIGHTNESS_MODE in service_data:
            br_mode = service_data.pop(ATTR_BRIGHTNESS_MODE)

        crop_area = {
            'active': False,
            'x': 0,
            'y': 0,
            'w': 0,
            'h': 0,
        }
        if ATTR_CROP_X in service_data:
            crop_area['x'] = service_data.pop(ATTR_CROP_X)
        if ATTR_CROP_Y in service_data:
            crop_area['y'] = service_data.pop(ATTR_CROP_Y)
        if ATTR_CROP_W in service_data:
            crop_area['w'] = service_data.pop(ATTR_CROP_W)
        if ATTR_CROP_H in service_data:
            crop_area['h'] = service_data.pop(ATTR_CROP_H)

        # Don't crop if height or width == 0
        if crop_area['w'] > 0 and crop_area['h'] > 0:
            crop_area['active'] = True

            if crop_area['x'] + crop_area['w'] > 100:
                crop_area['w'] = 100 - crop_area['x']
            if crop_area['y'] + crop_area['h'] > 100:
                crop_area['h'] = 100 - crop_area['y']

        try:
            if ATTR_URL in service_data:
                image_type = "URL"
                image_reference = service_data.pop(ATTR_URL)
                colorset = await async_extract_color_from_url(
                    image_reference, check_brightness, br_mode, crop_area
                )

            elif ATTR_PATH in service_data:
                image_type = "file path"
                image_reference = service_data.pop(ATTR_PATH)
                colorset = await hass.async_add_executor_job(
                    extract_color_from_path, image_reference, check_brightness, br_mode, crop_area
                )

            color = colorset["color"]
            if check_brightness:
                brightness = colorset["brightness"]

        except UnidentifiedImageError as ex:
            _LOGGER.error(
                "Bad image from %s '%s' provided, are you sure it's an image? %s",
                image_type,  # pylint: disable=used-before-assignment
                image_reference,
                ex,
            )
            return

        if color:
            service_data[ATTR_RGB_COLOR] = color

        if brightness:
            """Apply min and max brightness"""
            if br_min >= br_max:
                effective_brightness = br_min
            else:
                effective_brightness = br_min + ( (brightness / 255) * (br_max - br_min) )

            service_data[ATTR_BRIGHTNESS] = effective_brightness

        if color or brightness:
            await hass.services.async_call(
                LIGHT_DOMAIN, LIGHT_SERVICE_TURN_ON, service_data, blocking=True
            )


    hass.services.async_register(
        DOMAIN,
        SERVICE_TURN_ON,
        async_handle_service,
        schema=SERVICE_SCHEMA,
    )

    async def async_extract_color_from_url(url, check_brightness, br_mode, crop_area):
        """Handle call for URL based image."""
        if not hass.config.is_allowed_external_url(url):
            _LOGGER.error(
                "External URL '%s' is not allowed, please add to 'allowlist_external_urls'",
                url,
            )
            return None

        _LOGGER.debug("Getting predominant RGB from image URL '%s'", url)

        # Download the image into a buffer for ColorThief to check against
        try:
            session = aiohttp_client.async_get_clientsession(hass)

            async with async_timeout.timeout(10):
                response = await session.get(url)

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Failed to get ColorThief image due to HTTPError: %s", err)
            return None

        content = await response.content.read()
        with io.BytesIO(content) as _file:
            _file.name = "ambient_extractor.jpg"
            _file.seek(0)

            im = _get_cropped_image(_file, crop_area)

            color = _get_color_from_image(im) if crop_area['active'] else _get_color_from_file(_file)
            brightness = 0
            if check_brightness:
                brightness = _get_brightness(im, br_mode, color)

            return {
                "color": color,
                "brightness": brightness
            }

    def extract_color_from_path(file_path, check_brightness, br_mode, crop_area):
        """Handle call for local file based image."""
        if not hass.config.is_allowed_path(file_path):
            _LOGGER.error(
                "File path '%s' is not allowed, please add to 'allowlist_external_dirs'",
                file_path,
            )
            return None

        _LOGGER.debug("Getting predominant RGB from file path '%s'", file_path)
        _file = _get_file(file_path)
        im = _get_cropped_image(_file, crop_area)
        color = _get_color_from_image(im) if crop_area['active'] else _get_color_from_file(_file)

        brightness = 0
        if check_brightness:
            brightness = _get_brightness(im, br_mode, color)

        return {
            "color": color,
            "brightness": brightness
        }

    return True
