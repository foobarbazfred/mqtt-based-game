# MQTTベースのゲーム; MQTT 連打王
- MQTT 連打王は、MQTTを活用したリアルタイムボタン連打ゲームで、複数の場所でプレイできるように設計されています。プレイヤーはボタンをどれだけ速くタップするかで競い合い、スコアはMQTTを介して複数メンバ間で共有されます。
- このゲームは コントローラとプレイヤーで構成されます
   - コントローラはPCやRaspberry Pi等上でPython3で動かす必要があります（MQTT V5を使っています)
   - プレイヤーはRaspberry Pi Pico W  / Raspberry Pi Pico 2 W上のMicroPython 上で実行します
      - Pico /Pico 2である必要性は、スイッチの連打処理にPIOを使っているためです (マイコンとしてはRP2040/ RP2350)
      - MQTT通信は、umqtt.simpleを使っており MQTT V3です
      - スイッチのチャタリングを気にしないのであれば、PIOを外すことでESP32 + MicroPythonの組み合わせでも実行できると思います
