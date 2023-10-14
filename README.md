# Ambient Extractor

Fork of [color_extractor](https://www.home-assistant.io/integrations/color_extractor/), adding automatic brightness.

Like color_extractor, this integration will extract the predominant color from a given image and apply it to a target light. 
Additionally, overall brightness can be calculated and applied within adjustable limits. Useful as part of an automation.

### Service data attributes
| Attribute | Optional | Type | Default | Description |
|--|--|--|--|--|
| ambient_extract_url | * | URI | - | The full URL (including schema, `http://`, `https://`) of the image to process
| ambient_extract_path | * | String | - | The full path to the image file on local storage we’ll process
| entity_id | No | String | - | The light(s) we’ll set color and/or brightness of
| color_temperature | Yes | Int: 1.000 to 40.000 | 6.600 K | Apply color temperature correction
| brightness_auto | Yes | Boolean | False | Detect and set brightness
| brightness_mode | Yes | mean rms natural dominant | mean | Brightness calculation method. `mean` and `rms` use a grayscale image, `natural` uses perceived brightness, `dominant` the same color as for RGB (fastest).
| brightness_min  | Yes | Int: 0 to 255 | 2 | Minimal brightness. `< 2` means off for most devices.
| brightness_max  | Yes | Int: 0 to 255 | 70 | Maximal brightness, should be `> brightness_min`.
| crop_left | Yes | Int: 0 to 99 | 0 | Crop area: Left offset in % of image width. Default: 0
| crop_top | Yes | Int: 0 to 99 | 0 | Crop area: Top offset in % of image height. Default: 0
| crop_width | Yes | Int: 0 to 100 | 0 | Crop area: Width. Default: 0 (= no cropping)
| crop_height | Yes | Int: 0 to 100 | 0 | Crop area: Height. Default: 0 (= no cropping)

*) Either `ambient_extract_url`or `ambient_extract_path`needs to be set. 

**Please ensure any [external URLs](https://www.home-assistant.io/docs/configuration/basic/#allowlist_external_urls) or [external files](https://www.home-assistant.io/docs/configuration/basic/#allowlist_external_dirs) are authorized for use, you will receive error messages if this component is not allowed access to these external resources.**

Besides `rgb_color`and `brightness`, feel free to set [generic light](https://www.home-assistant.io/integrations/light/) attributes. For a static brightness setting, don't enable `brightness_auto`, just add a `brightness: ` or `brightness_pct:` value.

### Automation trigger recommendations

Slow sources like Android Debug Bridge (ADB) can take up to 15 seconds for a fully sized screenshot.
```yaml
trigger:
  - platform: time_pattern
    seconds: "*/15"
    minutes: "*"
    hours: "*"
  - platform: state
    entity_id: media_player.firetv
```

Ideal conditions using a fast source and scaled down images may allow for 2-3 times per second.
Enigma2 example: `http://enigma2/grab?format=png&mode=video&r=64`.
When using multiple ZHA light entities, consider creating a ZHA group to off-load your ZigBee network. 


## Installation

### Using HACS

1. Ensure that [HACS](https://github.com/hacs/integration) is installed.
2. Add Custom repository `https://github.com/xplus2/homeassistant-ambient-extractor`. Category `Integration`.
3. Install the "Ambient Extractor" integration.
4. Restart Home Assistant.

### Manual installation

1. Copy the folder `ambient_extractor` to `custom_components` in your Home Assistant `config` folder.
2. [Configure the integration](#configuration).
3. Restart Home Assistant.

## Configuration
Add the following line to your `configuration.yaml` (not needed when using HACS):

    ambient_extractor:


## Usage examples

```yaml
service: ambient_extractor.turn_on
data_template:
  ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=96"
  entity_id:
    - light.living_room_zha_group_0x0002
  transition: 0.4
  
  # bool, default: false
  brightness_auto: true
  
  # string(mean|rms|natural), default: mean
  brightness_mode: natural
  
  # 0-255, default: 2
  brightness_min: 2
  
  # 0-255, default: 70
  brightness_max: 70
```

### Using helper variables

```yaml
service: ambient_extractor.turn_on
data_template:
  ambient_extract_url: "http://127.0.0.1:8123{{ states.media_player.firetv.attributes.entity_picture }}"
  entity_id:
    - light.living_room_zha_group_0x0002
  transition: 0.3
  color_temperature: "{{ states('input_number.ambilight_color_temperature') }}"
  brightness_auto: true
  brightness_mode: natural
  brightness_min: "{{ states('input_number.ambilight_brightness_min') }}"
  brightness_max: "{{ states('input_number.ambilight_brightness_max') }}"
```
Create `ambilight_color_temperature` as Number from 1.000 to 40.000, step size 1.

Make sure that `allowlist_external_urls` contains `http://127.0.0.1:8123` when using the `entity_picture` attribute.


### Full automation YAML


#### Using a fast image source

Two times per second, if screenshots can be accessed fast enough. Tested with OpenATV on Vu+ Uno 4K SE.

```yaml
alias: Ambient Light enigma2
description: ""
trigger:
  - platform: time_pattern
    seconds: "*"
    minutes: "*"
    hours: "*"
condition:
  - condition: state
    entity_id: media_player.enigma2
    state: playing
action:
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=96"
      entity_id:
        - light.living_room_zha_group_0x0001
      transition: 0.3
      brightness_auto: true
  - delay:
      hours: 0
      minutes: 0
      seconds: 0
      milliseconds: 350
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=96"
      entity_id:
        - light.living_room_zha_group_0x0001
      transition: 0.3
      brightness_auto: true
mode: single
```

Left, right and ceiling using crop_*.

```yaml
alias: Ambient Light enigma2
description: ""
trigger:
  - platform: time_pattern
    seconds: "*"
    minutes: "*"
    hours: "*"
condition:
  - condition: state
    entity_id: media_player.enigma2
    state: playing
action:
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=64"
      entity_id:
        - light.living_room_tv_left
      transition: 0.6
      brightness_auto: true
      crop_left: 0
      crop_top: 0
      crop_width: 25
      crop_height: 100
  - delay:
      hours: 0
      minutes: 0
      seconds: 0
      milliseconds: 200
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=64"
      entity_id:
        - light.living_room_tv_right
      transition: 0.6
      brightness_auto: true
      crop_left: 75
      crop_width: 25
      crop_height: 100
  - delay:
      hours: 0
      minutes: 0
      seconds: 0
      milliseconds: 200
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=64"
      entity_id:
        - light.living_room_ceiling
      transition: 0.6
      brightness_auto: true
      crop_width: 100
      crop_height: 35
mode: single
```

`crop_width` and `crop_height` need values > 0 or cropping is disabled.

#### Using slower sources
```yaml
alias: Ambient Light FireTV
description: ""
trigger:
  - platform: state
    entity_id: media_player.firetv
action:
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://127.0.0.1:8123{{ states.media_player.firetv.attributes.entity_picture }}"
      entity_id:
        - light.living_room_floor_lamp
      transition: 2
      brightness_auto: true
      color_temperature: 5000
mode: single
```
