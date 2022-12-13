
# Ambient Extractor

Fork of [color_extractor](https://www.home-assistant.io/integrations/color_extractor/), adding automatic brightness.
  
## Installation

### Using HACS

1. Ensure that [HACS](https://github.com/hacs/integration) is installed.
2. Add Custom repository `https://github.com/xplus2/home-assistant-integrations`
3. Install the "Ambient Extractor" integration.
4. [Configure the integration](#configuration).
5. Restart Home Assistant.

### Manual installation

1. Copy the folder `ambient_extractor` to `custom_components` in your Home Assistant `config` folder.
2. [Configure the integration](#configuration).
3. Restart Home Assistant.

## Configuration
Add the following line to your `configuration.yaml`

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
  
  # 0-255, default: 100
  brightness_max: 70
```

### Using helper variables

```yaml
service: ambient_extractor.turn_on
data_template:
  ambient_extract_url: "{{ states.media_player.firetv.attributes.entity_picture }}"
  entity_id:
    - light.living_room_zha_group_0x0002
  transition: 0.3
  brightness_auto: true
  brightness_mode: natural
  brightness_min: "{{ states('input_number.ambilight_brightness_min') }}"
  brightness_max: "{{ states('input_number.ambilight_brightness_max') }}"
```

### Full automation YAML

```yaml

alias: Ambilight enigma2
description: ""
trigger:
  - platform: time_pattern
    seconds: "*"
    minutes: "*"
    hours: "*"
condition:
  - condition: or
    conditions:
      - condition: state
        entity_id: media_player.enigma2
        state: "on"
      - condition: state
        entity_id: media_player.enigma2
        state: playing
      - condition: state
        entity_id: media_player.enigma2
        state: paused
action:
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=96"
      entity_id:
        - light.living_room_zha_group_0x0002
      transition: 0.3
      brightness_auto: true
      brightness_mode: natural
      brightness_min: "{{ states('input_number.ambilight_brightness_min') }}"
      brightness_max: "{{ states('input_number.ambilight_brightness_max') }}"
  - delay:
      hours: 0
      minutes: 0
      seconds: 0
      milliseconds: 350
    enabled: true
  - service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: "http://enigma2/grab?format=png&mode=video&r=96"
      entity_id:
        - light.living_room_zha_group_0x0002
      transition: 0.3
      brightness_auto: true
      brightness_mode: natural
      brightness_min: "{{ states('input_number.ambilight_brightness_min') }}"
      brightness_max: "{{ states('input_number.ambilight_brightness_max') }}"
mode: single
```




