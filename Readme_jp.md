# MQTTベースの対戦型ゲーム; MQTT 連打王
- MQTT 連打王は、MQTTを活用した対戦型ボタン連打ゲームで、複数の場所でプレイできるように設計されています。プレイヤーは決められた時間内にどれだけ早くボタンをクリックできるかを競います。クリック数はMQTTを介して複数メンバ間で（ほぼ）リアルタイムに共有されます。
- このゲームは コントローラとプレイヤーで構成されます
   - コントローラ用プログラムはPCやRaspberry Pi等のPython3上で動かす必要があります（MQTT V5を使っているため)
   - プレイヤー用プログラムはRaspberry Pi Pico W  / Raspberry Pi Pico 2 W上のMicroPython 上で実行します
      - PIOを使ってスイッチのチャタリング除去とカウントを行っています。このため使えるマイコンボードは、Pico W/Pico 2 W　になります (マイコンとしてはRP2040/ RP2350)
      - MQTT通信は、umqtt.simpleを使っており MQTT V3です
      - スイッチのチャタリングを気にしないのであれば、PIOを外すことでESP32 + MicroPythonの組み合わせで実行できると思います
- 本ゲームはCQ出版 Interface誌  2025年10月号の解説記事として作成しました。モジュール構成やMQTTメッセージの体系等はInterface誌をご参照ください。
- インストールメモ(作成中)
   - MicroPythonではumqtt.simpleモジュールを使ってMQTT通信しています。umqtt.simpleは組み込みモジュールには含まれていませんので、以下の操作でモジュールを読み込んでください。
      ```
        >>> import mip
        >>> mip.install('umqtt.simple')
     ```
