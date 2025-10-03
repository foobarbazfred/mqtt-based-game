# MQTT-based Competitive Game: MQTT Button King

- MQTT Button King is a competitive button-mashing game utilizing MQTT, designed to be played in multiple locations. Players compete to press a button as many times as possible within a set time.
- The game consists of a controller and player modules:
   - The controller program must run on Python3 environments such as PC or Raspberry Pi (requires MQTT V5).
   - The player program runs on MicroPython on Raspberry Pi Pico W / Pico 2 W.
      - PIO is used to eliminate switch chattering and perform counting. Therefore, only Pico W/Pico 2 W microcontroller boards are supported.
      - MQTT communication uses umqtt.simple (MQTT V3).
      - If switch chattering is not a concern, you can remove PIO and likely run it with ESP32 + MicroPython.
- This game was created for an article in CQ Publishing’s Interface magazine, October 2025 issue. For module structure and MQTT message specifications, please refer to the magazine.
- Installation Notes (in progress):
   - MicroPython uses the umqtt.simple module for MQTT communication. umqtt.simple is not included in built-in modules, so please install it as follows:
      ```
      >>> import mip
      >>> mip.install('umqtt.simple')
      ```
### CQ Publishing Interface Magazine

- Interface October 2025 issue: https://interface.cqpub.co.jp/magazine/202510/
- <img src="https://interface.cqpub.co.jp/wp-content/uploads/MIF202510-scaled.jpg" width=100>