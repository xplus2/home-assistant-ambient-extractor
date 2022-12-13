# Ambient Extractor

Fork of [color_extractor](https://www.home-assistant.io/integrations/color_extractor/), adding automatic brightness.
  

# Usage examples

    service: ambient_extractor.turn_on
    data_template:
      ambient_extract_url: http://enigma2/grab?format=png&mode=video&r=96
      entity_id:
        - light.living_room_zha_group_0x0002
      transition: 0.4
      brightness_auto: true
      # mean, rms, natural
      brightness_mode: natural
      # 0-250
      brightness_min: 2
      # 0-250
      brightness_max: 70

Using helper variables:

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

