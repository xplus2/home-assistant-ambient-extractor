# v0.6.1
`color_temperature` now accepts values from 1.000 to 40.000 K, step size 1.
New default is 6.600

# v0.6
New features:
- color_temperature
  When using a receiver or other player as source, apply the tv's color temperature.

  Configuration:
  - color_temperature = []
# v0.5.2
Expanded crop functionality to color detection.
Changed "crop_offset_left" to "offset_left".
Changed "crop_offset_top" to "offset_top".

# v0.5.1
Fixed services.yaml

# v0.5
New features: 
- Limit brightness detection to an area of the source image.

  Configuration:
  - crop_offset_left = [0-100] in % width; default = 0
  - crop_offset_top = [0-100] in % height; default = 0
  - crop_width = [0-100] in % width; default = 0 == full image
  - crop_height = [ß-100] in % height; default = 0 == full image

# v0.4

Released 2023-02-20

- Removed experimental rgb_temperature

# v0.3

Released 2022-12-13

- Added rgb_temperature (-250; 250). Apply color correction on RGB values.

# v0.2

Released 2022-12-13

- Changed URL

# v0.1

Released 2022-12-13

- Initial release

