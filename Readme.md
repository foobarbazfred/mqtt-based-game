# MQTT-based Competitive Game: MQTT RENDA King

- MQTT RENDA King is a competitive button-mashing game that utilizes MQTT and is designed for play in multiple locations. Players compete to see how many times they can press a button within a set period.
- The game consists of a controller and player devices:
   - The controller program must run on Python 3 (such as on a PC or Raspberry Pi) because it uses MQTT V5.
   - The player program runs on MicroPython on Raspberry Pi Pico W or Raspberry Pi Pico 2 W.
      - PIO is used for switch debouncing and counting. Therefore, only Pico W/Pico 2 W microcontroller boards are supported.
      - MQTT communication uses umqtt.simple (MQTT V3).
      - If you do not require switch debouncing, you can remove PIO and likely run the game on ESP32 with MicroPython.
